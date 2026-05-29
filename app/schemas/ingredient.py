from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class IngredientBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    quantity: float = Field(gt=0, le=999999)
    unit: str = Field(default="unidad", min_length=1, max_length=40)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("name", "unit")
    @classmethod
    def strip_non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El campo no puede estar vacio")
        return value


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    quantity: float | None = Field(default=None, gt=0, le=999999)
    unit: str | None = Field(default=None, min_length=1, max_length=40)
    notes: str | None = Field(default=None, max_length=500)

    @field_validator("name", "unit")
    @classmethod
    def strip_optional(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("El campo no puede estar vacio")
        return value


class IngredientRead(IngredientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

