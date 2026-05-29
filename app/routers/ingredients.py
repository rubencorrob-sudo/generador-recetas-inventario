from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ingredient import Ingredient
from app.models.user import User
from app.schemas.ingredient import IngredientCreate, IngredientRead, IngredientUpdate
from app.schemas.recipe import InventorySummary

router = APIRouter(prefix="/api/ingredients", tags=["ingredients"])


@router.get("", response_model=list[IngredientRead])
def list_ingredients(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[Ingredient]:
    return list(
        db.scalars(
            select(Ingredient)
            .where(Ingredient.owner_id == current_user.id)
            .order_by(Ingredient.name.asc())
        )
    )


@router.get("/summary", response_model=InventorySummary)
def inventory_summary(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> InventorySummary:
    ingredients = list(
        db.scalars(
            select(Ingredient)
            .where(Ingredient.owner_id == current_user.id)
            .order_by(Ingredient.created_at.desc())
        )
    )
    total_units = sum(float(item.quantity) for item in ingredients)
    suggestions: list[str] = []
    if len(ingredients) < 3:
        suggestions.append("Agrega al menos 3 ingredientes para recetas mas variadas.")
    if not any(item.name.lower() in {"huevo", "huevos", "pollo", "atun", "carne"} for item in ingredients):
        suggestions.append("Incluye una fuente de proteina para mejorar las opciones.")
    if not any(item.name.lower() in {"arroz", "pasta", "papa", "yuca", "pan"} for item in ingredients):
        suggestions.append("Agrega una base como arroz, pasta, papa o pan.")
    if not suggestions:
        suggestions.append("Inventario listo para generar una receta completa.")

    inventory_score = min(100, 30 + len(ingredients) * 12)
    return InventorySummary(
        total_items=len(ingredients),
        total_units=round(total_units, 2),
        most_recent=ingredients[0].name if ingredients else None,
        inventory_score=inventory_score,
        suggestions=suggestions,
    )


@router.post("", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
def create_ingredient(
    payload: IngredientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Ingredient:
    ingredient = Ingredient(owner_id=current_user.id, **payload.model_dump())
    db.add(ingredient)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.put("/{ingredient_id}", response_model=IngredientRead)
def update_ingredient(
    ingredient_id: int,
    payload: IngredientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Ingredient:
    ingredient = db.get(Ingredient, ingredient_id)
    if ingredient is None or ingredient.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(ingredient, key, value)
    db.commit()
    db.refresh(ingredient)
    return ingredient


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(
    ingredient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    ingredient = db.get(Ingredient, ingredient_id)
    if ingredient is None or ingredient.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    db.delete(ingredient)
    db.commit()
