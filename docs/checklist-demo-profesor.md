# Checklist rapido de demo para sustentacion

Este archivo resume el orden recomendado para mostrar el proyecto al profesor
sin perder tiempo buscando pantallas o archivos.

## Enlaces principales

- Repositorio: https://github.com/rubencorrob-sudo/generador-recetas-inventario
- Aplicacion: https://www.recetasruben.xyz
- Swagger: https://www.recetasruben.xyz/docs
- Salud del servicio: `/health`

## Flujo de demostracion

1. Abrir la aplicacion en produccion.
2. Registrar o iniciar sesion con un usuario de prueba.
3. Agregar productos de canasta familiar al inventario.
4. Revisar el resumen del inventario y las recomendaciones automaticas.
5. Generar una receta con IA desde el formulario de preferencias.
6. Mostrar el desglose de ingredientes disponibles, faltantes, opcionales y basicos.
7. Marcar una receta como favorita y asignar una calificacion.
8. Abrir Swagger para evidenciar los endpoints REST.
9. Mostrar Docker Compose para explicar los servicios `db`, `app` y `caddy`.
10. Mostrar el Caddyfile para explicar dominio propio y SSL.

## Archivos clave para abrir en Visual Studio Code

- `app/main.py`: punto de entrada, routers y endpoint de salud.
- `app/config.py`: variables de entorno y configuracion de OpenRouter.
- `app/database.py`: conexion a base de datos con SQLAlchemy.
- `app/routers/auth.py`: registro, login y usuario actual.
- `app/routers/ingredients.py`: CRUD del inventario.
- `app/routers/recipes.py`: recomendaciones, generacion, favoritos y ratings.
- `app/services/llm_service.py`: prompt, llamada a OpenRouter y validacion JSON.
- `app/services/recommendation_service.py`: motor local de recomendaciones.
- `docker-compose.yml`: PostgreSQL, FastAPI y Caddy.
- `deploy/Caddyfile`: dominio, proxy inverso y SSL.

## Frase corta para cerrar

La arquitectura final es: navegador -> dominio con SSL en Caddy -> FastAPI con
Uvicorn -> PostgreSQL. OpenRouter se usa como proveedor externo para generar
recetas estructuradas en JSON a partir del inventario del usuario.
