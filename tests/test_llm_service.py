import pytest
from decimal import Decimal
from types import SimpleNamespace

from app.services.llm_service import (
    LLMServiceError,
    build_recipe_prompt,
    parse_recipe_response,
)
from app.schemas.recipe import RecipeGenerateRequest


def test_build_recipe_prompt_contains_inventory_and_json_contract():
    prompt = build_recipe_prompt(
        [
            {"name": "Huevos", "quantity": 4, "unit": "unidad", "notes": "frescos"},
            {"name": "Arroz", "quantity": 1, "unit": "taza", "notes": None},
        ],
        RecipeGenerateRequest(servings=4, objective="alta en proteina", cuisine="costena"),
    )

    assert "Huevos: 4 unidad" in prompt
    assert "Arroz: 1 taza" in prompt
    assert "Porciones: 4" in prompt
    assert "alta en proteina" in prompt
    assert "costena" in prompt
    assert '"nombre_plato"' in prompt
    assert '"nutricion_estimada"' in prompt
    assert '"pasos_preparacion"' in prompt
    assert "Responde exclusivamente con JSON valido" in prompt


def test_build_recipe_prompt_accepts_orm_like_objects_without_notes():
    prompt = build_recipe_prompt(
        [
            SimpleNamespace(
                name="Papa", quantity=Decimal("3.00"), unit="unidad", notes=None
            )
        ]
    )

    assert "Papa: 3 unidad" in prompt


def test_parse_recipe_response_accepts_fenced_json():
    content = """
```json
{
  "nombre_plato": "Arroz con huevo",
  "ingredientes": [{"name": "Arroz", "quantity": "1 taza"}],
  "pasos_preparacion": ["Cocina el arroz", "Sirve con huevo"],
  "tiempo_estimado": "25 minutos",
  "nivel_dificultad": "Facil"
}
```
"""

    recipe = parse_recipe_response(content)

    assert recipe.name == "Arroz con huevo"
    assert recipe.ingredients[0].name == "Arroz"
    assert recipe.difficulty == "Facil"


def test_parse_recipe_response_rejects_missing_required_fields():
    with pytest.raises(LLMServiceError):
        parse_recipe_response('{"nombre_plato": "Incompleta"}')
