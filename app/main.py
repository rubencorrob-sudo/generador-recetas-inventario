from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import auth, ingredients, pages, recipes


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Generador de Recetas con Inventario",
    description="API REST para inventario de ingredientes y recetas generadas por LLM.",
    version="1.0.0",
    lifespan=lifespan,
)


app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(ingredients.router)
app.include_router(recipes.router)
