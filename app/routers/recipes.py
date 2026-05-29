from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ingredient import Ingredient
from app.models.rating import Rating
from app.models.recipe import Recipe
from app.models.user import User
from app.schemas.recipe import (
    FavoriteUpdate,
    RatingCreate,
    RatingRead,
    RecipeGenerateRequest,
    RecipeRecommendation,
    RecipeRead,
)
from app.services.llm_service import LLMServiceError, generate_recipe_from_inventory
from app.services.recommendation_service import recommend_recipes

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


def _read_recipe(recipe: Recipe, current_user_id: int) -> RecipeRead:
    user_rating = next(
        (rating for rating in recipe.ratings if rating.user_id == current_user_id), None
    )
    data = {
        "id": recipe.id,
        "name": recipe.name,
        "description": recipe.description,
        "servings": recipe.servings or 1,
        "ingredients": recipe.ingredients or [],
        "steps": recipe.steps or [],
        "missing_ingredients": recipe.missing_ingredients or [],
        "tips": recipe.tips or [],
        "nutrition": recipe.nutrition or {},
        "tags": recipe.tags or [],
        "estimated_time": recipe.estimated_time,
        "difficulty": recipe.difficulty,
        "is_favorite": bool(recipe.is_favorite),
        "created_at": recipe.created_at,
        "rating": RatingRead.model_validate(user_rating) if user_rating else None,
    }
    return RecipeRead.model_validate(data)


@router.get("", response_model=list[RecipeRead])
def list_recipes(
    search: str | None = Query(default=None, max_length=120),
    favorite: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[RecipeRead]:
    statement = (
        select(Recipe)
        .options(selectinload(Recipe.ratings))
        .where(Recipe.owner_id == current_user.id)
    )
    if search:
        statement = statement.where(Recipe.name.ilike(f"%{search}%"))
    if favorite is not None:
        statement = statement.where(Recipe.is_favorite.is_(favorite))
    statement = statement.order_by(Recipe.created_at.desc())
    recipes = list(
        db.scalars(statement)
    )
    return [_read_recipe(recipe, current_user.id) for recipe in recipes]


@router.get("/recommendations", response_model=list[RecipeRecommendation])
def recommendations(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[RecipeRecommendation]:
    inventory = list(
        db.scalars(
            select(Ingredient)
            .where(Ingredient.owner_id == current_user.id)
            .order_by(Ingredient.name.asc())
        )
    )
    return recommend_recipes(inventory)


@router.post("/generate", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
async def generate_recipe(
    payload: RecipeGenerateRequest = Body(default_factory=RecipeGenerateRequest),
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> RecipeRead:
    inventory = list(
        db.scalars(
            select(Ingredient)
            .where(Ingredient.owner_id == current_user.id)
            .order_by(Ingredient.name.asc())
        )
    )
    if not inventory:
        raise HTTPException(
            status_code=400,
            detail="Agrega al menos un ingrediente antes de generar una receta",
        )

    try:
        result = await generate_recipe_from_inventory(inventory, payload)
    except LLMServiceError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    generated = result.recipe
    recipe = Recipe(
        owner_id=current_user.id,
        name=generated.name,
        description=generated.description,
        servings=generated.servings,
        ingredients=[item.model_dump() for item in generated.ingredients],
        steps=generated.steps,
        missing_ingredients=generated.missing_ingredients,
        tips=generated.tips,
        nutrition=generated.nutrition,
        tags=generated.tags,
        estimated_time=generated.estimated_time,
        difficulty=generated.difficulty,
        is_favorite=False,
        prompt=result.prompt,
        raw_response=result.raw_response,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    recipe.ratings = []
    return _read_recipe(recipe, current_user.id)


@router.patch("/{recipe_id}/favorite", response_model=RecipeRead)
def update_favorite(
    recipe_id: int,
    payload: FavoriteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecipeRead:
    recipe = db.scalar(
        select(Recipe)
        .options(selectinload(Recipe.ratings))
        .where(Recipe.id == recipe_id, Recipe.owner_id == current_user.id)
    )
    if recipe is None:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    recipe.is_favorite = payload.is_favorite
    db.commit()
    db.refresh(recipe)
    return _read_recipe(recipe, current_user.id)


@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecipeRead:
    recipe = db.scalar(
        select(Recipe)
        .options(selectinload(Recipe.ratings))
        .where(Recipe.id == recipe_id, Recipe.owner_id == current_user.id)
    )
    if recipe is None:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return _read_recipe(recipe, current_user.id)


@router.post("/{recipe_id}/ratings", response_model=RatingRead)
def rate_recipe(
    recipe_id: int,
    payload: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Rating:
    recipe = db.scalar(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.owner_id == current_user.id)
    )
    if recipe is None:
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    rating = db.scalar(
        select(Rating).where(
            Rating.recipe_id == recipe_id, Rating.user_id == current_user.id
        )
    )
    if rating is None:
        rating = Rating(
            recipe_id=recipe_id,
            user_id=current_user.id,
            score=payload.score,
            comment=payload.comment,
        )
        db.add(rating)
    else:
        rating.score = payload.score
        rating.comment = payload.comment
    db.commit()
    db.refresh(rating)
    return rating


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    recipe = db.scalar(
        select(Recipe).where(Recipe.id == recipe_id, Recipe.owner_id == current_user.id)
    )
    if recipe is None:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    db.delete(recipe)
    db.commit()
