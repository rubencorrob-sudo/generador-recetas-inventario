from dataclasses import dataclass

from app.models.ingredient import Ingredient
from app.schemas.recipe import IngredientBreakdownItem, RecipeRecommendation


BASIC_PANTRY = {"agua", "sal", "pimienta", "aceite"}
ALIASES = {
    "huevo": {"huevo", "huevos"},
    "tomate": {"tomate", "tomates"},
    "arroz": {"arroz"},
    "pasta": {"pasta", "espagueti", "spaghetti", "macarron"},
    "queso": {"queso", "quesito"},
    "pollo": {"pollo", "pechuga"},
    "atun": {"atun", "atún"},
    "papa": {"papa", "papas", "patata"},
    "platano": {"platano", "plátano", "guineo"},
    "pan": {"pan", "tajado"},
    "arepa": {"arepa", "arepas"},
    "leche": {"leche"},
    "avena": {"avena"},
    "frijol": {"frijol", "frijoles", "caraotas"},
    "lenteja": {"lenteja", "lentejas"},
    "cebolla": {"cebolla", "cebollin", "cebollín"},
    "cilantro": {"cilantro"},
    "lechuga": {"lechuga"},
    "yuca": {"yuca"},
    "carne": {"carne", "res", "molida"},
    "cerdo": {"cerdo", "costilla", "lomo"},
    "pescado": {"pescado", "tilapia", "mojarra"},
    "harina": {"harina", "harina de trigo"},
    "maiz": {"maiz", "maíz", "mazorca", "choclo"},
    "garbanzo": {"garbanzo", "garbanzos"},
    "arveja": {"arveja", "arvejas"},
    "zanahoria": {"zanahoria", "zanahorias"},
    "repollo": {"repollo", "col"},
    "pepino": {"pepino", "cohombro"},
    "pimenton": {"pimenton", "pimentón", "pimiento"},
    "ajo": {"ajo"},
    "limon": {"limon", "limón"},
    "banano": {"banano", "banana", "cambur"},
    "manzana": {"manzana", "manzanas"},
    "naranja": {"naranja", "naranjas"},
    "panela": {"panela"},
    "azucar": {"azucar", "azúcar"},
    "cafe": {"cafe", "café"},
    "chocolate": {"chocolate", "cocoa", "cacao"},
    "mantequilla": {"mantequilla", "margarina"},
    "yogur": {"yogur", "yogurt"},
    "crema": {"crema", "crema de leche"},
    "salchicha": {"salchicha", "salchichas"},
    "jamon": {"jamon", "jamón"},
    "mango": {"mango"},
    "aguacate": {"aguacate"},
    "calabaza": {"ahuyama", "calabaza", "zapallo"},
    "apio": {"apio"},
}


@dataclass(frozen=True)
class RecipeTemplate:
    title: str
    description: str
    required: tuple[str, ...]
    optional: tuple[str, ...]
    estimated_time: str
    difficulty: str
    tags: tuple[str, ...]


TEMPLATES = [
    RecipeTemplate(
        title="Arroz salteado con huevo y tomate",
        description="Plato rapido, economico y perfecto para aprovechar sobras.",
        required=("arroz", "huevo", "tomate"),
        optional=("queso", "cebolla", "cilantro"),
        estimated_time="20 minutos",
        difficulty="Facil",
        tags=("rapida", "economica", "alta en proteina"),
    ),
    RecipeTemplate(
        title="Tortilla de queso y tomate",
        description="Tortilla suave con relleno cremoso y vegetales frescos.",
        required=("huevo", "queso", "tomate"),
        optional=("cebolla", "pimenton", "cilantro"),
        estimated_time="18 minutos",
        difficulty="Facil",
        tags=("desayuno", "alta en proteina", "una sarten"),
    ),
    RecipeTemplate(
        title="Bowl casero de arroz completo",
        description="Base de arroz con proteina, vegetales y topping fresco.",
        required=("arroz", "huevo"),
        optional=("tomate", "queso", "aguacate", "lechuga"),
        estimated_time="25 minutos",
        difficulty="Facil",
        tags=("balanceada", "meal prep", "sin compras grandes"),
    ),
    RecipeTemplate(
        title="Pasta cremosa de inventario",
        description="Pasta rapida con lo que haya en la nevera y acabado cremoso.",
        required=("pasta", "queso"),
        optional=("tomate", "leche", "pollo", "atun"),
        estimated_time="22 minutos",
        difficulty="Media",
        tags=("cremosa", "cena", "comfort food"),
    ),
    RecipeTemplate(
        title="Ensalada tibia con proteina",
        description="Opcion ligera que mezcla vegetales con una proteina disponible.",
        required=("tomate",),
        optional=("huevo", "queso", "lechuga", "pepino", "atun"),
        estimated_time="15 minutos",
        difficulty="Facil",
        tags=("ligera", "saludable", "rapida"),
    ),
    RecipeTemplate(
        title="Arepa rellena de nevera",
        description="Arepa practica con relleno caliente de queso, huevo o vegetales.",
        required=("arepa",),
        optional=("queso", "huevo", "tomate", "pollo"),
        estimated_time="16 minutos",
        difficulty="Facil",
        tags=("colombiana", "snack", "economica"),
    ),
    RecipeTemplate(
        title="Arroz con atun y tomate",
        description="Comida express con proteina y base rendidora.",
        required=("arroz", "atun"),
        optional=("tomate", "cebolla", "cilantro", "queso"),
        estimated_time="18 minutos",
        difficulty="Facil",
        tags=("rapida", "alta en proteina", "sin complicarse"),
    ),
    RecipeTemplate(
        title="Huevos pericos con arroz",
        description="Clasico colombiano para resolver desayuno, almuerzo o cena.",
        required=("huevo", "tomate", "cebolla"),
        optional=("arroz", "queso", "cilantro"),
        estimated_time="15 minutos",
        difficulty="Facil",
        tags=("colombiana", "desayuno", "economica"),
    ),
    RecipeTemplate(
        title="Papas salteadas con queso",
        description="Papas doradas con acabado cremoso y topping disponible.",
        required=("papa", "queso"),
        optional=("huevo", "tomate", "cebolla"),
        estimated_time="28 minutos",
        difficulty="Facil",
        tags=("contundente", "una sarten", "economica"),
    ),
    RecipeTemplate(
        title="Tortilla espanola sencilla",
        description="Tortilla gruesa de papa y huevo para compartir.",
        required=("papa", "huevo"),
        optional=("cebolla", "queso", "tomate"),
        estimated_time="35 minutos",
        difficulty="Media",
        tags=("familiar", "alta en proteina", "sin horno"),
    ),
    RecipeTemplate(
        title="Sandwich caliente de queso y huevo",
        description="Opcion rapida para usar pan, huevo y queso en pocos minutos.",
        required=("pan", "huevo", "queso"),
        optional=("tomate", "lechuga", "cebolla"),
        estimated_time="12 minutos",
        difficulty="Facil",
        tags=("snack", "rapida", "alta en proteina"),
    ),
    RecipeTemplate(
        title="Avena cremosa con fruta",
        description="Desayuno dulce, rendidor y facil de ajustar.",
        required=("avena", "leche"),
        optional=("banano", "canela", "azucar"),
        estimated_time="10 minutos",
        difficulty="Facil",
        tags=("desayuno", "dulce", "rapida"),
    ),
    RecipeTemplate(
        title="Lentejas guisadas rapidas",
        description="Guiso casero con buena proteina vegetal.",
        required=("lenteja", "tomate", "cebolla"),
        optional=("arroz", "papa", "zanahoria"),
        estimated_time="40 minutos",
        difficulty="Media",
        tags=("proteina vegetal", "casera", "meal prep"),
    ),
    RecipeTemplate(
        title="Frijoles express con arroz",
        description="Bowl rendidor con base de arroz y legumbre.",
        required=("frijol", "arroz"),
        optional=("tomate", "cebolla", "queso", "aguacate"),
        estimated_time="30 minutos",
        difficulty="Media",
        tags=("colombiana", "rendidor", "proteina vegetal"),
    ),
    RecipeTemplate(
        title="Pollo salteado con arroz",
        description="Plato principal completo con proteina y guarnicion.",
        required=("pollo", "arroz"),
        optional=("tomate", "cebolla", "pimenton", "cilantro"),
        estimated_time="30 minutos",
        difficulty="Media",
        tags=("almuerzo", "alta en proteina", "completa"),
    ),
    RecipeTemplate(
        title="Carne molida guisada",
        description="Guiso versatil para servir con arroz, arepa o papa.",
        required=("carne", "tomate", "cebolla"),
        optional=("arroz", "papa", "cilantro"),
        estimated_time="25 minutos",
        difficulty="Media",
        tags=("proteina", "almuerzo", "casera"),
    ),
    RecipeTemplate(
        title="Yuca dorada con hogao",
        description="Acompanamiento colombiano con tomate y cebolla.",
        required=("yuca", "tomate", "cebolla"),
        optional=("queso", "cilantro", "huevo"),
        estimated_time="32 minutos",
        difficulty="Media",
        tags=("colombiana", "acompanamiento", "vegetariana"),
    ),
    RecipeTemplate(
        title="Patacon con topping de nevera",
        description="Base crocante de platano con queso, huevo o hogao.",
        required=("platano",),
        optional=("queso", "huevo", "tomate", "cebolla"),
        estimated_time="24 minutos",
        difficulty="Media",
        tags=("colombiana", "crujiente", "snack"),
    ),
    RecipeTemplate(
        title="Omelette de inventario",
        description="Omelette flexible con los vegetales y quesos disponibles.",
        required=("huevo",),
        optional=("queso", "tomate", "cebolla", "lechuga"),
        estimated_time="12 minutos",
        difficulty="Facil",
        tags=("rapida", "alta en proteina", "desayuno"),
    ),
    RecipeTemplate(
        title="Arroz con queso gratinado",
        description="Arroz cremoso al sarten con queso derretido.",
        required=("arroz", "queso"),
        optional=("huevo", "tomate", "leche"),
        estimated_time="18 minutos",
        difficulty="Facil",
        tags=("comfort food", "economica", "sin horno"),
    ),
    RecipeTemplate(
        title="Sopa rapida de papa y huevo",
        description="Sopa casera sencilla para una comida caliente.",
        required=("papa", "huevo"),
        optional=("cebolla", "cilantro", "leche"),
        estimated_time="30 minutos",
        difficulty="Facil",
        tags=("sopa", "casera", "economica"),
    ),
    RecipeTemplate(
        title="Ensalada de arroz fria",
        description="Ensalada rendidora para aprovechar arroz y vegetales.",
        required=("arroz", "tomate"),
        optional=("atun", "huevo", "lechuga", "queso"),
        estimated_time="16 minutos",
        difficulty="Facil",
        tags=("fria", "meal prep", "rapida"),
    ),
    RecipeTemplate(
        title="Quesadilla casera de arepa",
        description="Arepa abierta con queso fundido y topping fresco.",
        required=("arepa", "queso"),
        optional=("huevo", "tomate", "cebolla"),
        estimated_time="14 minutos",
        difficulty="Facil",
        tags=("colombiana", "rapida", "quesuda"),
    ),
    RecipeTemplate(
        title="Pasta roja sencilla",
        description="Pasta con salsa rapida de tomate y toque de queso.",
        required=("pasta", "tomate"),
        optional=("queso", "cebolla", "atun", "pollo"),
        estimated_time="24 minutos",
        difficulty="Facil",
        tags=("cena", "italiana", "economica"),
    ),
    RecipeTemplate(
        title="Picadillo de papa y huevo",
        description="Salteado casero con cubos de papa, huevo y vegetales.",
        required=("papa", "huevo"),
        optional=("tomate", "cebolla", "queso"),
        estimated_time="26 minutos",
        difficulty="Facil",
        tags=("sarten", "economica", "contundente"),
    ),
    RecipeTemplate(
        title="Bowl costeño rapido",
        description="Base de arroz con huevo, queso y tomate para resolver en casa.",
        required=("arroz", "huevo", "queso"),
        optional=("tomate", "platano", "cilantro"),
        estimated_time="22 minutos",
        difficulty="Facil",
        tags=("costena", "completa", "alta en proteina"),
    ),
    RecipeTemplate(
        title="Garbanzo guisado con arroz",
        description="Guiso rendidor con legumbre, arroz y vegetales de base.",
        required=("garbanzo", "arroz"),
        optional=("tomate", "cebolla", "zanahoria", "cilantro"),
        estimated_time="35 minutos",
        difficulty="Media",
        tags=("proteina vegetal", "rendidor", "almuerzo"),
    ),
    RecipeTemplate(
        title="Arvejas con papa y zanahoria",
        description="Guiso casero suave para acompanar arroz o arepa.",
        required=("arveja", "papa"),
        optional=("zanahoria", "tomate", "cebolla"),
        estimated_time="32 minutos",
        difficulty="Media",
        tags=("casera", "vegetariana", "economica"),
    ),
    RecipeTemplate(
        title="Ensalada de repollo y zanahoria",
        description="Ensalada fresca, barata y perfecta para acompanar proteinas.",
        required=("repollo", "zanahoria"),
        optional=("limon", "pepino", "cilantro"),
        estimated_time="12 minutos",
        difficulty="Facil",
        tags=("fresca", "acompanamiento", "saludable"),
    ),
    RecipeTemplate(
        title="Sudado de pollo con papa",
        description="Plato tradicional con pollo, papa y guiso de tomate.",
        required=("pollo", "papa", "tomate"),
        optional=("cebolla", "yuca", "cilantro"),
        estimated_time="45 minutos",
        difficulty="Media",
        tags=("colombiana", "almuerzo", "tradicional"),
    ),
    RecipeTemplate(
        title="Cerdo salteado con yuca",
        description="Proteina dorada con acompanamiento de yuca y hogao.",
        required=("cerdo", "yuca"),
        optional=("tomate", "cebolla", "limon"),
        estimated_time="38 minutos",
        difficulty="Media",
        tags=("almuerzo", "contundente", "casera"),
    ),
    RecipeTemplate(
        title="Pescado con arroz y ensalada",
        description="Comida completa con pescado, arroz y vegetales frescos.",
        required=("pescado", "arroz"),
        optional=("limon", "lechuga", "tomate", "pepino"),
        estimated_time="30 minutos",
        difficulty="Media",
        tags=("saludable", "alta en proteina", "almuerzo"),
    ),
    RecipeTemplate(
        title="Sancocho sencillo de canasta",
        description="Sopa completa con tuberculos y la proteina disponible.",
        required=("papa", "yuca", "platano"),
        optional=("pollo", "carne", "cerdo", "cilantro"),
        estimated_time="60 minutos",
        difficulty="Media",
        tags=("colombiana", "familiar", "sopa"),
    ),
    RecipeTemplate(
        title="Mazorca salteada con queso",
        description="Maiz tierno con queso y toque de mantequilla.",
        required=("maiz", "queso"),
        optional=("mantequilla", "cilantro", "limon"),
        estimated_time="18 minutos",
        difficulty="Facil",
        tags=("snack", "vegetariana", "rapida"),
    ),
    RecipeTemplate(
        title="Arepuelas de harina",
        description="Frituras caseras sencillas con harina, huevo y leche.",
        required=("harina", "huevo"),
        optional=("leche", "queso", "azucar"),
        estimated_time="20 minutos",
        difficulty="Facil",
        tags=("desayuno", "economica", "casera"),
    ),
    RecipeTemplate(
        title="Pancakes de banano y avena",
        description="Desayuno dulce con pocos ingredientes y buena energia.",
        required=("banano", "avena", "huevo"),
        optional=("leche", "miel", "canela"),
        estimated_time="15 minutos",
        difficulty="Facil",
        tags=("desayuno", "dulce", "saludable"),
    ),
    RecipeTemplate(
        title="Colada de avena con panela",
        description="Bebida caliente y rendidora para desayuno o merienda.",
        required=("avena", "panela"),
        optional=("leche", "canela", "chocolate"),
        estimated_time="14 minutos",
        difficulty="Facil",
        tags=("bebida", "desayuno", "economica"),
    ),
    RecipeTemplate(
        title="Chocolate caliente con queso",
        description="Clasico desayuno colombiano con chocolate y queso.",
        required=("chocolate", "queso"),
        optional=("leche", "pan", "arepa"),
        estimated_time="12 minutos",
        difficulty="Facil",
        tags=("colombiana", "desayuno", "bebida"),
    ),
    RecipeTemplate(
        title="Cafe con pan tostado",
        description="Merienda rapida con cafe y pan dorado.",
        required=("cafe", "pan"),
        optional=("mantequilla", "queso", "panela"),
        estimated_time="8 minutos",
        difficulty="Facil",
        tags=("merienda", "rapida", "desayuno"),
    ),
    RecipeTemplate(
        title="Salchichas guisadas con arroz",
        description="Comida rapida con salchicha, tomate y arroz.",
        required=("salchicha", "arroz"),
        optional=("tomate", "cebolla", "pimenton"),
        estimated_time="20 minutos",
        difficulty="Facil",
        tags=("rapida", "economica", "almuerzo"),
    ),
    RecipeTemplate(
        title="Arroz con jamon y queso",
        description="Arroz salteado con cubitos de jamon y queso.",
        required=("arroz", "jamon", "queso"),
        optional=("huevo", "tomate", "cebolla"),
        estimated_time="18 minutos",
        difficulty="Facil",
        tags=("rapida", "nevera", "alta en proteina"),
    ),
    RecipeTemplate(
        title="Crema de ahuyama",
        description="Sopa cremosa con ahuyama y lacteo disponible.",
        required=("calabaza",),
        optional=("crema", "leche", "queso", "cebolla"),
        estimated_time="35 minutos",
        difficulty="Facil",
        tags=("sopa", "vegetariana", "suave"),
    ),
    RecipeTemplate(
        title="Ensalada tropical de mango",
        description="Ensalada fresca con mango, tomate y toque citrico.",
        required=("mango", "limon"),
        optional=("lechuga", "pepino", "queso"),
        estimated_time="10 minutos",
        difficulty="Facil",
        tags=("fresca", "tropical", "rapida"),
    ),
    RecipeTemplate(
        title="Yogur con fruta y avena",
        description="Desayuno frio, rapido y balanceado.",
        required=("yogur", "avena"),
        optional=("banano", "manzana", "mango"),
        estimated_time="6 minutos",
        difficulty="Facil",
        tags=("desayuno", "sin coccion", "saludable"),
    ),
    RecipeTemplate(
        title="Compota rapida de manzana",
        description="Postre casero suave con fruta y panela o azucar.",
        required=("manzana",),
        optional=("panela", "azucar", "canela", "limon"),
        estimated_time="18 minutos",
        difficulty="Facil",
        tags=("postre", "fruta", "economica"),
    ),
    RecipeTemplate(
        title="Jugo natural de naranja",
        description="Bebida fresca para acompanar desayunos y almuerzos.",
        required=("naranja",),
        optional=("limon", "azucar", "panela"),
        estimated_time="8 minutos",
        difficulty="Facil",
        tags=("bebida", "fruta", "rapida"),
    ),
    RecipeTemplate(
        title="Guacamole casero con arepa",
        description="Aguacate machacado con limon para servir con arepa o pan.",
        required=("aguacate", "limon"),
        optional=("arepa", "pan", "tomate", "cebolla"),
        estimated_time="10 minutos",
        difficulty="Facil",
        tags=("snack", "fresco", "vegetariana"),
    ),
    RecipeTemplate(
        title="Arroz con verduras de canasta",
        description="Arroz salteado con zanahoria, cebolla, pimenton o lo disponible.",
        required=("arroz", "zanahoria"),
        optional=("cebolla", "pimenton", "arveja", "maiz"),
        estimated_time="24 minutos",
        difficulty="Facil",
        tags=("vegetariana", "economica", "rendidor"),
    ),
    RecipeTemplate(
        title="Pepino relleno frio",
        description="Opcion fresca con pepino y proteina o lacteo disponible.",
        required=("pepino",),
        optional=("atun", "queso", "yogur", "limon"),
        estimated_time="12 minutos",
        difficulty="Facil",
        tags=("fresca", "sin coccion", "ligera"),
    ),
    RecipeTemplate(
        title="Hogao base para acompanamientos",
        description="Salsa colombiana de tomate y cebolla para arroz, arepa o yuca.",
        required=("tomate", "cebolla"),
        optional=("ajo", "cilantro", "limon"),
        estimated_time="15 minutos",
        difficulty="Facil",
        tags=("colombiana", "base", "acompanamiento"),
    ),
]


def normalize(value: str) -> str:
    return value.strip().lower()


def ingredient_names(inventory: list[Ingredient]) -> set[str]:
    return {normalize(item.name) for item in inventory}


def has_ingredient(available: set[str], expected: str) -> bool:
    expected = normalize(expected)
    expected_terms = ALIASES.get(expected, {expected})
    return any(
        term in item or item in term
        for item in available
        for term in expected_terms
    )


def build_breakdown(
    template: RecipeTemplate, available: set[str]
) -> list[IngredientBreakdownItem]:
    breakdown: list[IngredientBreakdownItem] = []
    for name in template.required:
        status = "disponible" if has_ingredient(available, name) else "faltante"
        detail = "Ya esta en tu inventario" if status == "disponible" else "Necesario para la receta"
        breakdown.append(IngredientBreakdownItem(name=name, status=status, detail=detail))
    for name in template.optional:
        status = "disponible" if has_ingredient(available, name) else "opcional"
        detail = (
            "Lo puedes usar para mejorar la receta"
            if status == "disponible"
            else "Puede omitirse o reemplazarse"
        )
        breakdown.append(IngredientBreakdownItem(name=name, status=status, detail=detail))
    for name in sorted(BASIC_PANTRY):
        breakdown.append(
            IngredientBreakdownItem(
                name=name, status="basico", detail="Se asume disponible en cocina"
            )
        )
    return breakdown


def recommend_recipes(inventory: list[Ingredient], limit: int = 18) -> list[RecipeRecommendation]:
    available = ingredient_names(inventory)
    recommendations: list[RecipeRecommendation] = []
    for template in TEMPLATES:
        matched_required = [
            name for name in template.required if has_ingredient(available, name)
        ]
        matched_optional = [
            name for name in template.optional if has_ingredient(available, name)
        ]
        missing_required = [
            name for name in template.required if not has_ingredient(available, name)
        ]
        required_score = (
            len(matched_required) / len(template.required) * 80
            if template.required
            else 80
        )
        optional_score = (
            len(matched_optional) / len(template.optional) * 20
            if template.optional
            else 20
        )
        score = int(round(required_score + optional_score))
        if score == 0 and available:
            score = 12
        elif score == 0:
            score = 5
        reason = (
            "Muy buena opcion: tienes todos los ingredientes clave."
            if not missing_required
            else f"Te faltan pocos ingredientes clave: {', '.join(missing_required)}."
        )
        recommendations.append(
            RecipeRecommendation(
                title=template.title,
                description=template.description,
                match_score=score,
                matched_ingredients=matched_required + matched_optional,
                missing_ingredients=missing_required,
                estimated_time=template.estimated_time,
                difficulty=template.difficulty,
                tags=list(template.tags),
                reason=reason,
                breakdown=build_breakdown(template, available),
            )
        )

    recommendations.sort(
        key=lambda item: (item.match_score, -len(item.missing_ingredients)), reverse=True
    )
    return recommendations[:limit]
