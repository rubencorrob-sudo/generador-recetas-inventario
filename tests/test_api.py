from app.schemas.recipe import GeneratedRecipe
from app.services.llm_service import LLMRecipeResult


def test_home_page_renders_login_forms(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Iniciar sesion" in response.text
    assert "Crear cuenta" in response.text


def test_register_login_and_create_ingredient(client):
    register = client.post(
        "/api/auth/register",
        json={"email": "lina@example.com", "password": "secret-123"},
    )
    assert register.status_code == 201
    token = register.json()["access_token"]

    login = client.post(
        "/api/auth/login",
        json={"email": "lina@example.com", "password": "secret-123"},
    )
    assert login.status_code == 200

    ingredient = client.post(
        "/api/ingredients",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Papa", "quantity": 3, "unit": "unidad"},
    )
    assert ingredient.status_code == 201
    assert ingredient.json()["name"] == "Papa"


def test_generate_recipe_endpoint_saves_history(client, auth_headers, monkeypatch):
    client.post(
        "/api/ingredients",
        headers=auth_headers,
        json={"name": "Pasta", "quantity": 250, "unit": "g"},
    )

    async def fake_generate_recipe(inventory, options=None):
        recipe = GeneratedRecipe.model_validate(
            {
                "nombre_plato": "Pasta rapida",
                "descripcion": "Lista en pocos minutos.",
                "porciones": 3,
                "ingredientes": [{"name": "Pasta", "quantity": "250 g"}],
                "pasos_preparacion": ["Hervir", "Servir"],
                "consejos": ["Usa el agua de coccion para ligar la salsa"],
                "nutricion_estimada": {"calorias": "420 kcal"},
                "etiquetas": ["rapida"],
                "tiempo_estimado": "15 minutos",
                "nivel_dificultad": "Facil",
            }
        )
        return LLMRecipeResult(recipe=recipe, prompt="prompt", raw_response="{}")

    monkeypatch.setattr(
        "app.routers.recipes.generate_recipe_from_inventory", fake_generate_recipe
    )

    generated = client.post(
        "/api/recipes/generate",
        headers=auth_headers,
        json={"servings": 3, "objective": "economica"},
    )
    assert generated.status_code == 201
    assert generated.json()["name"] == "Pasta rapida"
    assert generated.json()["servings"] == 3
    assert generated.json()["tags"] == ["rapida"]

    recipes = client.get("/api/recipes", headers=auth_headers)
    assert recipes.status_code == 200
    assert len(recipes.json()) == 1


def test_rate_recipe_endpoint(client, auth_headers, monkeypatch):
    client.post(
        "/api/ingredients",
        headers=auth_headers,
        json={"name": "Queso", "quantity": 100, "unit": "g"},
    )

    async def fake_generate_recipe(inventory, options=None):
        recipe = GeneratedRecipe.model_validate(
            {
                "nombre_plato": "Queso gratinado",
                "ingredientes": [{"name": "Queso", "quantity": "100 g"}],
                "pasos_preparacion": ["Calentar", "Dorar"],
                "tiempo_estimado": "10 minutos",
                "nivel_dificultad": "Facil",
            }
        )
        return LLMRecipeResult(recipe=recipe, prompt="prompt", raw_response="{}")

    monkeypatch.setattr(
        "app.routers.recipes.generate_recipe_from_inventory", fake_generate_recipe
    )
    recipe_id = client.post("/api/recipes/generate", headers=auth_headers).json()["id"]

    rating = client.post(
        f"/api/recipes/{recipe_id}/ratings",
        headers=auth_headers,
        json={"score": 5, "comment": "Muy util"},
    )

    assert rating.status_code == 200
    assert rating.json()["score"] == 5


def test_inventory_summary_and_favorite_recipe(client, auth_headers, monkeypatch):
    client.post(
        "/api/ingredients",
        headers=auth_headers,
        json={"name": "Huevos", "quantity": 4, "unit": "unidad"},
    )
    client.post(
        "/api/ingredients",
        headers=auth_headers,
        json={"name": "Arroz", "quantity": 1, "unit": "taza"},
    )

    summary = client.get("/api/ingredients/summary", headers=auth_headers)
    assert summary.status_code == 200
    assert summary.json()["total_items"] == 2
    assert summary.json()["inventory_score"] > 0

    async def fake_generate_recipe(inventory, options=None):
        recipe = GeneratedRecipe.model_validate(
            {
                "nombre_plato": "Arroz con huevos",
                "ingredientes": [{"name": "Huevos", "quantity": "4 unidad"}],
                "pasos_preparacion": ["Cocinar", "Servir"],
                "tiempo_estimado": "20 minutos",
                "nivel_dificultad": "Facil",
            }
        )
        return LLMRecipeResult(recipe=recipe, prompt="prompt", raw_response="{}")

    monkeypatch.setattr(
        "app.routers.recipes.generate_recipe_from_inventory", fake_generate_recipe
    )
    recipe_id = client.post("/api/recipes/generate", headers=auth_headers).json()["id"]

    favorite = client.patch(
        f"/api/recipes/{recipe_id}/favorite",
        headers=auth_headers,
        json={"is_favorite": True},
    )

    assert favorite.status_code == 200
    assert favorite.json()["is_favorite"] is True


def test_recommendations_include_match_score_and_breakdown(client, auth_headers):
    for ingredient in [
        {"name": "Arroz", "quantity": 1, "unit": "taza"},
        {"name": "Huevos", "quantity": 4, "unit": "unidad"},
        {"name": "Tomate", "quantity": 3, "unit": "unidad"},
    ]:
        client.post("/api/ingredients", headers=auth_headers, json=ingredient)

    response = client.get("/api/recipes/recommendations", headers=auth_headers)

    assert response.status_code == 200
    recommendations = response.json()
    assert len(recommendations) >= 15
    assert recommendations[0]["match_score"] >= 80
    statuses = {item["status"] for item in recommendations[0]["breakdown"]}
    assert "disponible" in statuses
    assert "basico" in statuses


def test_recommendations_cover_more_family_basket_products(client, auth_headers):
    for ingredient in [
        {"name": "Garbanzo", "quantity": 1, "unit": "lb"},
        {"name": "Papa", "quantity": 4, "unit": "unidad"},
        {"name": "Zanahoria", "quantity": 2, "unit": "unidad"},
        {"name": "Repollo", "quantity": 1, "unit": "unidad"},
    ]:
        client.post("/api/ingredients", headers=auth_headers, json=ingredient)

    response = client.get("/api/recipes/recommendations", headers=auth_headers)

    assert response.status_code == 200
    titles = {item["title"] for item in response.json()}
    assert "Garbanzo guisado con arroz" in titles
    assert "Ensalada de repollo y zanahoria" in titles
