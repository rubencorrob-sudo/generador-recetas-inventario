import json
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import httpx
from pydantic import ValidationError

from app.config import settings
from app.models.ingredient import Ingredient
from app.schemas.recipe import GeneratedRecipe, RecipeGenerateRequest


class LLMServiceError(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMRecipeResult:
    recipe: GeneratedRecipe
    prompt: str
    raw_response: str


def _item_value(item: Ingredient | dict[str, Any], key: str) -> Any:
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key)


def _format_quantity(value: Any) -> str:
    if isinstance(value, Decimal):
        if value == value.to_integral():
            return str(value.quantize(Decimal("1")))
        return format(value.normalize(), "f")
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def build_recipe_prompt(
    inventory: list[Ingredient | dict[str, Any]],
    options: RecipeGenerateRequest | None = None,
) -> str:
    options = options or RecipeGenerateRequest()
    items = []
    for item in inventory:
        name = _item_value(item, "name")
        quantity = _item_value(item, "quantity")
        unit = _item_value(item, "unit")
        notes = _item_value(item, "notes")
        note_text = f" ({notes})" if notes else ""
        items.append(f"- {name}: {_format_quantity(quantity)} {unit}{note_text}")

    inventory_text = "\n".join(items)
    cuisine = options.cuisine or "cocina casera latinoamericana"
    restrictions = options.dietary_restrictions or "sin restricciones declaradas"
    max_time = (
        f"{options.max_time_minutes} minutos"
        if options.max_time_minutes
        else "sin limite estricto"
    )
    strictness = (
        "Usa exclusivamente el inventario, salvo basicos como agua, sal, pimienta y aceite."
        if options.strict_inventory
        else "Puedes proponer pocos ingredientes adicionales y marcarlos como faltantes."
    )
    extra = options.extra_instructions or "sin instrucciones adicionales"

    return f"""
Eres un chef practico para cocina casera. Crea una receta usando principalmente
el inventario disponible del usuario. Puedes asumir agua, sal, pimienta y aceite,
pero evita ingredientes nuevos salvo que sean opcionales.

Inventario disponible:
{inventory_text}

Preferencias del usuario:
- Porciones: {options.servings}
- Tipo de comida: {options.meal_type}
- Objetivo: {options.objective}
- Estilo de cocina: {cuisine}
- Tiempo maximo: {max_time}
- Restricciones alimentarias: {restrictions}
- Regla de inventario: {strictness}
- Instrucciones extra: {extra}

Responde exclusivamente con JSON valido y sin texto adicional. Usa exactamente
estas claves:
{{
  "nombre_plato": "string",
  "descripcion": "string corto, apetitoso y especifico",
  "porciones": {options.servings},
  "ingredientes": [
    {{"name": "ingrediente", "quantity": "cantidad con unidad"}}
  ],
  "pasos_preparacion": ["paso 1", "paso 2"],
  "ingredientes_faltantes": ["solo si hacen falta, si no []"],
  "consejos": ["consejo practico 1", "consejo practico 2"],
  "nutricion_estimada": {{
    "calorias": "aproximado por porcion",
    "proteina": "aproximado por porcion",
    "carbohidratos": "aproximado por porcion",
    "grasas": "aproximado por porcion"
  }},
  "etiquetas": ["rapida", "economica", "alta en proteina"],
  "tiempo_estimado": "string",
  "nivel_dificultad": "Facil | Media | Dificil"
}}
""".strip()


def _extract_json_object(content: str) -> dict[str, Any]:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise LLMServiceError("La respuesta del LLM no contiene JSON")
        return json.loads(match.group(0))


def parse_recipe_response(content: str) -> GeneratedRecipe:
    try:
        payload = _extract_json_object(content)
        return GeneratedRecipe.model_validate(payload)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise LLMServiceError("No fue posible parsear la receta generada") from exc


def _fallback_recipe(
    inventory: list[Ingredient | dict[str, Any]],
    options: RecipeGenerateRequest | None = None,
) -> GeneratedRecipe:
    options = options or RecipeGenerateRequest()
    first_items = []
    for item in inventory[:5]:
        name = _item_value(item, "name")
        quantity = _item_value(item, "quantity")
        unit = _item_value(item, "unit")
        first_items.append(
            {"name": name, "quantity": f"{_format_quantity(quantity)} {unit}"}
        )
    payload = {
        "nombre_plato": "Salteado rapido de inventario",
        "descripcion": "Una preparacion simple que aprovecha lo disponible sin compras extra.",
        "porciones": options.servings,
        "ingredientes": first_items,
        "pasos_preparacion": [
            "Lava, pela y corta los ingredientes disponibles.",
            "Calienta una sarten con un poco de aceite a fuego medio.",
            "Agrega primero los ingredientes mas firmes y luego los mas blandos.",
            "Ajusta sal y pimienta, cocina hasta que todo este tierno y sirve caliente.",
        ],
        "ingredientes_faltantes": [],
        "consejos": [
            "Sirve con limon o hierbas si tienes disponibles.",
            "Si quieres mas textura, deja dorar los ingredientes sin moverlos durante un minuto.",
        ],
        "nutricion_estimada": {
            "calorias": "350-450 kcal",
            "proteina": "12-18 g",
            "carbohidratos": "45-60 g",
            "grasas": "10-16 g",
        },
        "etiquetas": ["rapida", "economica", "sin compras extra"],
        "tiempo_estimado": "25 minutos",
        "nivel_dificultad": "Facil",
    }
    return GeneratedRecipe.model_validate(payload)


async def generate_recipe_from_inventory(
    inventory: list[Ingredient | dict[str, Any]],
    options: RecipeGenerateRequest | None = None,
) -> LLMRecipeResult:
    if not inventory:
        raise LLMServiceError("El inventario esta vacio")

    prompt = build_recipe_prompt(inventory, options)
    if settings.llm_dry_run or not settings.openrouter_api_key:
        recipe = _fallback_recipe(inventory, options)
        raw_response = recipe.model_dump_json(by_alias=True)
        return LLMRecipeResult(recipe=recipe, prompt=prompt, raw_response=raw_response)

    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {
                "role": "system",
                "content": "Respondes solo JSON valido para una app de recetas.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://recetas.example.com",
        "X-Title": settings.app_name,
    }

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(
                f"{settings.openrouter_base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
    except (httpx.HTTPError, KeyError, IndexError, TypeError) as exc:
        raise LLMServiceError("Error consultando el proveedor LLM") from exc

    recipe = parse_recipe_response(content)
    return LLMRecipeResult(recipe=recipe, prompt=prompt, raw_response=content)
