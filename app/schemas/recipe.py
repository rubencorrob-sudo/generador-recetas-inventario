from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class RecipeIngredient(BaseModel):
    name: str
    quantity: str


class RecipeGenerateRequest(BaseModel):
    servings: int = Field(default=2, ge=1, le=12)
    meal_type: str = Field(default="almuerzo", max_length=40)
    objective: str = Field(default="rapida y sabrosa", max_length=80)
    cuisine: str | None = Field(default=None, max_length=80)
    max_time_minutes: int | None = Field(default=35, ge=5, le=240)
    dietary_restrictions: str | None = Field(default=None, max_length=160)
    extra_instructions: str | None = Field(default=None, max_length=240)
    strict_inventory: bool = True

    @field_validator(
        "meal_type", "objective", "cuisine", "dietary_restrictions", "extra_instructions"
    )
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        return value or None


class GeneratedRecipe(BaseModel):
    name: str = Field(alias="nombre_plato")
    description: str | None = Field(default=None, alias="descripcion")
    servings: int = Field(default=2, alias="porciones")
    ingredients: list[RecipeIngredient] = Field(alias="ingredientes")
    steps: list[str] = Field(alias="pasos_preparacion")
    missing_ingredients: list[str] = Field(default_factory=list, alias="ingredientes_faltantes")
    tips: list[str] = Field(default_factory=list, alias="consejos")
    nutrition: dict[str, str] = Field(default_factory=dict, alias="nutricion_estimada")
    tags: list[str] = Field(default_factory=list, alias="etiquetas")
    estimated_time: str = Field(alias="tiempo_estimado")
    difficulty: str = Field(alias="nivel_dificultad")

    model_config = {"populate_by_name": True}


class RatingCreate(BaseModel):
    score: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=500)


class RatingRead(BaseModel):
    id: int
    score: int
    comment: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FavoriteUpdate(BaseModel):
    is_favorite: bool


class InventorySummary(BaseModel):
    total_items: int
    total_units: float
    most_recent: str | None = None
    inventory_score: int
    suggestions: list[str]


class IngredientBreakdownItem(BaseModel):
    name: str
    status: str
    detail: str


class RecipeRecommendation(BaseModel):
    title: str
    description: str
    match_score: int
    matched_ingredients: list[str]
    missing_ingredients: list[str]
    estimated_time: str
    difficulty: str
    tags: list[str]
    reason: str
    breakdown: list[IngredientBreakdownItem]


class RecipeRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    servings: int = 1
    ingredients: list[dict]
    steps: list[str]
    missing_ingredients: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)
    nutrition: dict[str, str] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    estimated_time: str
    difficulty: str
    is_favorite: bool = False
    created_at: datetime
    rating: RatingRead | None = None

    model_config = {"from_attributes": True}
