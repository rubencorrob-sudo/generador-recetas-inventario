from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "guia-sustentacion-codigo.docx"

BLUE = RGBColor(46, 116, 181)
DARK_BLUE = RGBColor(31, 77, 120)
INK = RGBColor(32, 35, 31)
MUTED = RGBColor(89, 89, 89)
HEADER_FILL = "E8EEF5"
SOFT_FILL = "F4F6F9"


def set_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_margins(cell, top=80, bottom=80, start=120, end=120) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin_name, value in {
        "top": top,
        "bottom": bottom,
        "start": start,
        "end": end,
    }.items():
        node = tc_mar.find(qn(f"w:{margin_name}"))
        if node is None:
            node = OxmlElement(f"w:{margin_name}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_width(table, width_dxa: int = 9360, indent_dxa: int = 120) -> None:
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(width_dxa))
    tbl_w.set(qn("w:type"), "dxa")

    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), str(indent_dxa))
    tbl_ind.set(qn("w:type"), "dxa")


def keep_row_together(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = tr_pr.find(qn("w:cantSplit"))
    if cant_split is None:
        tr_pr.append(OxmlElement("w:cantSplit"))


def repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = tr_pr.find(qn("w:tblHeader"))
    if tbl_header is None:
        tbl_header = OxmlElement("w:tblHeader")
        tr_pr.append(tbl_header)
    tbl_header.set(qn("w:val"), "true")


def set_cell_text(cell, text: str, bold: bool = False, size: float = 10.2) -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    set_cell_margins(cell)


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    table.autofit = False
    set_table_width(table)
    repeat_table_header(table.rows[0])

    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        cell.width = Inches(widths[index])
        set_cell_text(cell, header, bold=True)
        set_shading(cell, HEADER_FILL)

    for row in rows:
        new_row = table.add_row()
        keep_row_together(new_row)
        cells = new_row.cells
        for index, value in enumerate(row):
            cells[index].width = Inches(widths[index])
            set_cell_text(cells[index], value, bold=index == 0)
    doc.add_paragraph()


def add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        paragraph = doc.add_paragraph(style="List Bullet")
        paragraph.paragraph_format.space_after = Pt(4)
        paragraph.paragraph_format.line_spacing = 1.25
        paragraph.add_run(item)


def add_numbered(doc: Document, items: list[str]) -> None:
    for item in items:
        paragraph = doc.add_paragraph(style="List Bullet")
        paragraph.paragraph_format.space_after = Pt(4)
        paragraph.paragraph_format.line_spacing = 1.25
        paragraph.add_run(item)


def add_callout(doc: Document, title: str, body: str) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    table.autofit = False
    set_table_width(table)
    keep_row_together(table.rows[0])
    cell = table.rows[0].cells[0]
    set_shading(cell, SOFT_FILL)
    set_cell_margins(cell, top=120, bottom=120, start=160, end=160)
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(2)
    paragraph.paragraph_format.keep_together = True
    run = paragraph.add_run(title)
    run.bold = True
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.color.rgb = DARK_BLUE
    paragraph.add_run("\n" + body)
    for run_item in paragraph.runs:
        run_item.font.name = "Calibri"
        if run_item.font.size is None:
            run_item.font.size = Pt(10.5)
    doc.add_paragraph()


def style_document(doc: Document) -> None:
    section = doc.sections[0]
    section.orientation = WD_ORIENT.PORTRAIT
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    normal.font.color.rgb = INK
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.25

    heading_tokens = [
        ("Heading 1", 16, BLUE, 18, 10),
        ("Heading 2", 13, BLUE, 14, 7),
        ("Heading 3", 12, DARK_BLUE, 10, 5),
    ]
    for style_name, size, color, before, after in heading_tokens:
        style = styles[style_name]
        style.font.name = "Calibri"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = color
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.line_spacing = 1.25

    for list_style in ["List Bullet", "List Number"]:
        style = styles[list_style]
        style.font.name = "Calibri"
        style.font.size = Pt(11)
        style.paragraph_format.left_indent = Inches(0.375)
        style.paragraph_format.first_line_indent = Inches(-0.188)
        style.paragraph_format.space_after = Pt(4)
        style.paragraph_format.line_spacing = 1.25


def add_title(doc: Document) -> None:
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    title.paragraph_format.space_after = Pt(4)
    run = title.add_run("Guia para explicar el codigo en sustentacion")
    run.font.name = "Calibri"
    run.font.size = Pt(23)
    run.font.bold = True
    run.font.color.rgb = INK

    subtitle = doc.add_paragraph()
    subtitle.paragraph_format.space_after = Pt(10)
    run = subtitle.add_run("Generador de Recetas con Inventario | FastAPI + PostgreSQL + OpenRouter + Docker")
    run.font.name = "Calibri"
    run.font.size = Pt(12.5)
    run.font.color.rgb = BLUE

    meta = doc.add_paragraph()
    meta.paragraph_format.space_after = Pt(12)
    run = meta.add_run(
        "Integrantes: Sean Paul Marquez Toro, Reyner David Barbosa de la Rosa y Ruben Andres Corro Blanco"
    )
    run.font.name = "Calibri"
    run.font.size = Pt(10.5)
    run.font.color.rgb = MUTED


def build() -> None:
    doc = Document()
    style_document(doc)
    add_title(doc)

    add_callout(
        doc,
        "Respuesta de apertura",
        "El proyecto es una aplicacion web donde cada usuario registra los ingredientes que tiene en casa. "
        "Con ese inventario, la app recomienda recetas por coincidencia de productos de canasta familiar y tambien "
        "puede generar una receta completa con un LLM usando OpenRouter.",
    )

    doc.add_heading("1. Mapa rapido del proyecto", level=1)
    add_table(
        doc,
        ["Ruta", "Funcion", "Que decir si la abre el profesor"],
        [
            ["app/main.py", "Punto de entrada FastAPI", "Aqui se crea la app, se monta /static, se inicializa la base de datos y se registran los routers."],
            ["app/config.py", "Variables de entorno", "Lee DATABASE_URL, SECRET_KEY, OPENROUTER_API_KEY, OPENROUTER_MODEL y LLM_DRY_RUN sin quemar secretos en codigo."],
            ["app/database.py", "Conexion SQLAlchemy", "Crea el engine, maneja sesiones por peticion y crea tablas al iniciar."],
            ["app/models/", "Tablas de negocio", "Define usuarios, ingredientes, recetas y calificaciones con relaciones entre ellas."],
            ["app/schemas/", "Validacion Pydantic", "Controla datos de entrada y salida: correos, cantidades, porciones, ratings y estructura JSON de recetas."],
            ["app/routers/", "Endpoints REST", "Agrupa autenticacion, ingredientes, recetas y pagina principal."],
            ["app/services/", "Logica interna", "Separa seguridad, recomendaciones locales y generacion con OpenRouter."],
            ["templates/ + static/", "Frontend", "HTML, CSS y JS consumen la API con fetch y renderizan la experiencia visual."],
            ["docker-compose.yml", "Produccion", "Levanta PostgreSQL, FastAPI y Caddy para dominio y SSL."],
            ["deploy/Caddyfile", "Proxy y HTTPS", "Caddy recibe el dominio, emite SSL y envia el trafico al contenedor app:8000."],
        ],
        [1.55, 1.55, 3.4],
    )

    doc.add_heading("2. Como arranca la aplicacion", level=1)
    doc.add_paragraph(
        "El punto de entrada es app/main.py. Alli se instancia FastAPI con titulo, descripcion y version. "
        "Tambien se define un lifespan que ejecuta init_db() al iniciar, por eso la aplicacion prepara las tablas "
        "antes de atender peticiones."
    )
    add_bullets(
        doc,
        [
            "app.mount('/static', ...) publica CSS, JS, imagenes y favicon.",
            "include_router(pages.router) sirve la interfaz web en /.",
            "include_router(auth.router) registra endpoints de registro, login y /me.",
            "include_router(ingredients.router) registra el CRUD del inventario.",
            "include_router(recipes.router) registra recomendaciones, generacion, favoritos y ratings.",
        ],
    )
    add_callout(
        doc,
        "Frase lista",
        "La app arranca en app/main.py. FastAPI conecta los routers, monta archivos estaticos y ejecuta init_db() "
        "para preparar la base de datos al inicio.",
    )

    doc.add_heading("3. Configuracion y variables de entorno", level=1)
    doc.add_paragraph(
        "La configuracion esta centralizada en app/config.py mediante una clase Settings. Esto permite cambiar "
        "base de datos, modelo LLM, dominio o llaves sin modificar el codigo fuente."
    )
    add_bullets(
        doc,
        [
            "DATABASE_URL: cadena de conexion a PostgreSQL en produccion o SQLite local.",
            "SECRET_KEY: clave usada para firmar tokens JWT.",
            "OPENROUTER_API_KEY: token del proveedor LLM.",
            "OPENROUTER_MODEL: modelo usado; por defecto openai/gpt-4o-mini.",
            "LLM_DRY_RUN: modo de prueba para generar fallback sin llamar al proveedor externo.",
        ],
    )
    add_callout(
        doc,
        "Frase lista",
        "No dejamos secretos quemados. El codigo lee las variables desde el entorno, y Docker Compose las inyecta al contenedor.",
    )

    doc.add_heading("4. Base de datos y modelos", level=1)
    doc.add_paragraph(
        "La base se maneja con SQLAlchemy. En app/database.py se crea el engine y SessionLocal. Cada endpoint recibe "
        "una sesion mediante Depends(get_db), lo que abre la conexion, ejecuta la operacion y la cierra al final."
    )
    add_table(
        doc,
        ["Modelo", "Tabla", "Explicacion"],
        [
            ["User", "users", "Guarda email, nombre, password_hash y relaciones con inventario, recetas y ratings."],
            ["Ingredient", "ingredients", "Guarda cada ingrediente con owner_id, nombre, cantidad, unidad, notas y fechas."],
            ["Recipe", "recipes", "Guarda recetas generadas: nombre, descripcion, ingredientes JSON, pasos, faltantes, tips, nutricion, tags y prompt."],
            ["Rating", "ratings", "Guarda calificacion de 1 a 5 y comentario; tiene restriccion unica por usuario y receta."],
        ],
        [1.3, 1.45, 4.75],
    )
    add_callout(
        doc,
        "Frase lista",
        "Cada ingrediente y receta pertenece a un usuario por owner_id. Por eso las consultas filtran por el usuario autenticado y no mezclan datos.",
    )

    doc.add_heading("5. Validacion con Pydantic", level=1)
    doc.add_paragraph(
        "Los schemas en app/schemas/ validan datos antes de guardarlos o devolverlos. Esto evita entradas invalidas "
        "y tambien define la forma oficial de las respuestas de la API."
    )
    add_bullets(
        doc,
        [
            "UserCreate valida correo y exige contrasena minima de 8 caracteres.",
            "IngredientCreate exige nombre no vacio, cantidad mayor que cero y unidad valida.",
            "RecipeGenerateRequest limita porciones entre 1 y 12 y tiempo entre 5 y 240 minutos.",
            "GeneratedRecipe define el JSON que debe entregar el LLM: nombre_plato, ingredientes, pasos, nutricion, etiquetas y dificultad.",
            "RatingCreate restringe la calificacion entre 1 y 5.",
        ],
    )
    add_callout(
        doc,
        "Frase lista",
        "Pydantic es la primera defensa de calidad: valida entradas del usuario y valida tambien la estructura que viene del LLM.",
    )

    doc.add_heading("6. Autenticacion y seguridad", level=1)
    doc.add_paragraph(
        "El registro y login estan en app/routers/auth.py. La seguridad esta en app/services/security.py. "
        "La contrasena no se guarda en texto plano: se guarda como hash PBKDF2-SHA256 con salt. Cuando el usuario inicia sesion, "
        "la app genera un token JWT firmado."
    )
    add_numbered(
        doc,
        [
            "El usuario se registra en /api/auth/register.",
            "La contrasena pasa por hash_password() y se guarda como password_hash.",
            "En login se compara con verify_password().",
            "Si las credenciales son correctas, create_access_token() genera un Bearer token.",
            "get_current_user() lee el token, lo valida y retorna el usuario autenticado.",
        ],
    )
    add_callout(
        doc,
        "Frase lista",
        "Las rutas protegidas usan Depends(get_current_user). Asi el backend sabe quien esta haciendo la peticion y puede filtrar sus datos.",
    )

    doc.add_heading("7. Endpoints de ingredientes", level=1)
    doc.add_paragraph(
        "El router app/routers/ingredients.py implementa el inventario personal. Permite listar, crear, editar y eliminar ingredientes. "
        "Tambien tiene /summary para calcular metricas del inventario."
    )
    add_bullets(
        doc,
        [
            "GET /api/ingredients: lista solo ingredientes del usuario actual.",
            "POST /api/ingredients: crea un ingrediente asociado al current_user.id.",
            "PUT /api/ingredients/{id}: actualiza si el ingrediente pertenece al usuario.",
            "DELETE /api/ingredients/{id}: elimina si pertenece al usuario.",
            "GET /api/ingredients/summary: calcula total de items, unidades, score y sugerencias.",
        ],
    )

    doc.add_heading("8. Recomendaciones locales", level=1)
    doc.add_paragraph(
        "Las recomendaciones estan en app/services/recommendation_service.py. No dependen del LLM; usan plantillas locales "
        "de recetas con productos de canasta familiar. Esto hace que respondan rapido y siempre funcionen."
    )
    add_numbered(
        doc,
        [
            "Se normalizan los nombres de ingredientes del inventario.",
            "Se comparan contra alias: huevo/huevos, platano/platano, atun/atún, etc.",
            "Cada plantilla define ingredientes requeridos y opcionales.",
            "Se calcula match_score con hasta 80 puntos por requeridos y 20 por opcionales.",
            "Se construye un breakdown: disponible, faltante, opcional y basico.",
            "Se ordenan las mejores opciones y se devuelven hasta 18 recomendaciones.",
        ],
    )
    add_callout(
        doc,
        "Frase lista",
        "Las recomendaciones son un motor local de reglas y plantillas. El LLM se usa despues, cuando el usuario quiere generar una receta completa.",
    )

    doc.add_heading("9. Generacion con OpenRouter", level=1)
    doc.add_paragraph(
        "La generacion esta en app/services/llm_service.py y el endpoint que la llama esta en app/routers/recipes.py. "
        "El backend no manda una conversacion abierta; construye un prompt controlado y exige una respuesta JSON."
    )
    add_numbered(
        doc,
        [
            "El usuario presiona Generar receta IA.",
            "El frontend envia opciones: porciones, tipo de comida, objetivo, tiempo, restricciones e instrucciones extra.",
            "El backend consulta el inventario del usuario.",
            "build_recipe_prompt() arma el prompt con inventario y contrato JSON.",
            "generate_recipe_from_inventory() llama a OpenRouter en /chat/completions.",
            "parse_recipe_response() extrae y valida el JSON con GeneratedRecipe.",
            "La receta se guarda en la tabla recipes con prompt y raw_response para trazabilidad.",
        ],
    )
    add_callout(
        doc,
        "Frase lista",
        "El LLM no decide la estructura de la aplicacion. Solo genera el contenido de la receta, y el backend valida que venga en el formato esperado.",
    )

    doc.add_heading("10. Historial, favoritos y calificaciones", level=1)
    doc.add_paragraph(
        "El router de recetas tambien permite consultar historial, buscar por texto, filtrar favoritas, marcar favoritas, calificar y eliminar recetas."
    )
    add_bullets(
        doc,
        [
            "GET /api/recipes devuelve recetas del usuario con su rating si existe.",
            "PATCH /api/recipes/{id}/favorite actualiza is_favorite.",
            "POST /api/recipes/{id}/ratings crea o actualiza la calificacion del usuario.",
            "DELETE /api/recipes/{id} elimina la receta si pertenece al usuario.",
        ],
    )

    doc.add_heading("11. Frontend: HTML, CSS y JavaScript", level=1)
    doc.add_paragraph(
        "La interfaz esta en templates/index.html y static/app.js. El frontend guarda el token en localStorage y usa fetch "
        "para consumir la API REST."
    )
    add_bullets(
        doc,
        [
            "state guarda token, usuario, ingredientes, recetas, recomendaciones y resumen.",
            "api() agrega el header Authorization: Bearer cuando hay sesion.",
            "loadAll() carga ingredientes, recetas, resumen y recomendaciones en paralelo.",
            "renderIngredients(), renderRecommendations() y renderRecipes() pintan la pantalla.",
            "Los chips de canasta familiar agregan productos comunes rapidamente.",
            "El boton Generar receta IA envia POST /api/recipes/generate.",
        ],
    )
    add_callout(
        doc,
        "Frase lista",
        "El frontend es una interfaz que consume una API real. No trabaja con datos falsos: todo sale de los endpoints de FastAPI.",
    )

    doc.add_heading("12. Docker, dominio y SSL", level=1)
    doc.add_paragraph(
        "El proyecto se ejecuta en produccion con Docker Compose. Hay tres servicios principales: db, app y caddy."
    )
    add_table(
        doc,
        ["Servicio", "Tecnologia", "Funcion"],
        [
            ["db", "postgres:16-alpine", "Base de datos PostgreSQL con volumen persistente."],
            ["app", "FastAPI + Uvicorn", "Backend Python que expone la API y la interfaz."],
            ["caddy", "Caddy 2", "Proxy inverso, HTTPS automatico y redireccion hacia app:8000."],
        ],
        [1.25, 1.85, 3.4],
    )
    add_callout(
        doc,
        "Frase lista",
        "La arquitectura en produccion es: navegador -> dominio con SSL en Caddy -> contenedor FastAPI -> PostgreSQL. OpenRouter queda como proveedor externo.",
    )

    doc.add_heading("13. Flujo completo de una receta", level=1)
    add_numbered(
        doc,
        [
            "Usuario inicia sesion y recibe token JWT.",
            "Agrega ingredientes al inventario.",
            "La app muestra resumen y recomendaciones locales.",
            "Usuario configura preferencias y genera receta.",
            "FastAPI consulta inventario, arma prompt y llama OpenRouter.",
            "La respuesta JSON se valida con Pydantic.",
            "La receta se guarda en PostgreSQL.",
            "El frontend actualiza historial, permite marcar favorita, calificar y copiar.",
        ],
    )

    doc.add_heading("14. Preguntas tipicas del profesor", level=1)
    add_table(
        doc,
        ["Pregunta", "Respuesta corta"],
        [
            ["Que LLM usan?", "OpenRouter como proveedor, con modelo configurable por OPENROUTER_MODEL; por defecto openai/gpt-4o-mini."],
            ["Donde esta el prompt?", "En build_recipe_prompt() dentro de app/services/llm_service.py."],
            ["Como protegen datos?", "Con JWT, hash de contrasenas y filtros por owner_id en ingredientes y recetas."],
            ["Que base de datos usan?", "PostgreSQL en produccion mediante Docker Compose; SQLite solo como fallback local si no hay DATABASE_URL."],
            ["Las recomendaciones son IA?", "Son un motor local por reglas y plantillas; la IA se usa para generar la receta completa."],
            ["Como validan la respuesta del LLM?", "Se exige JSON, se parsea y se valida con el schema GeneratedRecipe de Pydantic."],
            ["Como se despliega?", "Docker Compose levanta db, app y caddy. Caddy gestiona dominio, proxy inverso y SSL."],
            ["Como prueban el proyecto?", "Hay tests en tests/ para API, validaciones, recomendaciones y servicio LLM. El ultimo resultado local fue 14 passed."],
        ],
        [2.05, 4.45],
    )

    doc.add_heading("15. Mini guion para decirlo de corrido", level=1)
    doc.add_paragraph(
        "El proyecto es un generador de recetas con inventario. Primero el usuario se registra e inicia sesion. "
        "Luego agrega ingredientes, que se guardan en PostgreSQL asociados a su usuario. Con ese inventario, la app "
        "calcula recomendaciones locales usando plantillas de canasta familiar y un puntaje de coincidencia. Si el usuario "
        "quiere una receta completa, FastAPI arma un prompt controlado y consulta OpenRouter. La respuesta debe venir en JSON, "
        "se valida con Pydantic y se guarda como historial. El frontend consume los endpoints REST con fetch, muestra recetas, "
        "favoritos, calificaciones y desglose de ingredientes. En produccion todo corre con Docker Compose: PostgreSQL, FastAPI "
        "y Caddy, que maneja el dominio y SSL."
    )

    doc.add_heading("16. Checklist antes de abrir Visual Studio", level=1)
    add_bullets(
        doc,
        [
            "Abrir app/main.py para mostrar punto de entrada.",
            "Abrir app/routers/recipes.py para mostrar generacion y guardado.",
            "Abrir app/services/llm_service.py para mostrar prompt y OpenRouter.",
            "Abrir app/services/recommendation_service.py para mostrar recomendaciones de canasta familiar.",
            "Abrir app/models/ para mostrar entidades de base de datos.",
            "Abrir docker-compose.yml para mostrar PostgreSQL, app y Caddy.",
            "Abrir /docs en produccion para mostrar Swagger.",
        ],
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
