import pytest
from pydantic import ValidationError

from app.schemas.ingredient import IngredientCreate


def test_ingredient_name_cannot_be_blank():
    with pytest.raises(ValidationError):
        IngredientCreate(name="   ", quantity=1, unit="kg")


def test_ingredient_quantity_must_be_positive():
    with pytest.raises(ValidationError):
        IngredientCreate(name="Arroz", quantity=0, unit="kg")


def test_ingredient_trims_name_and_unit():
    ingredient = IngredientCreate(name="  Tomate  ", quantity=2, unit=" unidad ")

    assert ingredient.name == "Tomate"
    assert ingredient.unit == "unidad"

