import json

from fastapi import APIRouter, Depends, Request
from fastapi import Response
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.ingredient import Ingredient
from app.models.user import User
from app.schemas.auth import UserRead
from app.services.security import create_access_token, hash_password

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "index.html", {"app_name": settings.app_name}
    )


@router.head("/", include_in_schema=False)
def home_head() -> Response:
    return Response(status_code=200)


@router.get("/demo", response_class=HTMLResponse, include_in_schema=False)
def demo_login(db: Session = Depends(get_db)) -> HTMLResponse:
    email = "demo@recetasruben.xyz"
    password = "Demo12345"
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(
            email=email,
            full_name="Demo Profesor",
            password_hash=hash_password(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    demo_items = [
        ("Arroz", 1, "taza"),
        ("Huevos", 6, "unidad"),
        ("Tomate", 3, "unidad"),
        ("Queso", 1, "unidad"),
        ("Pollo", 1, "libra"),
        ("Cebolla", 2, "unidad"),
        ("Papa", 4, "unidad"),
    ]
    existing = {
        item.name.lower(): item
        for item in db.scalars(select(Ingredient).where(Ingredient.owner_id == user.id))
    }
    for name, quantity, unit in demo_items:
        ingredient = existing.get(name.lower())
        if ingredient is None:
            db.add(
                Ingredient(
                    owner_id=user.id,
                    name=name,
                    quantity=quantity,
                    unit=unit,
                    notes="demo canasta familiar",
                )
            )
    db.commit()

    token = create_access_token(subject=str(user.id), extra={"email": user.email})
    user_json = UserRead.model_validate(user).model_dump_json()
    html = f"""<!doctype html>
<html lang="es">
  <head><meta charset="utf-8"><title>Entrando demo...</title></head>
  <body>
    <script>
      localStorage.setItem("recipe_token", {json.dumps(token)});
      localStorage.setItem("recipe_user", {json.dumps(user_json)});
      location.replace("/");
    </script>
    Entrando a la demo...
  </body>
</html>"""
    return HTMLResponse(html)


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse("static/favicon.ico")
