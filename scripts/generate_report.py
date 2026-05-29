from pathlib import Path
from textwrap import wrap

import fitz
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "informe-proyecto-recetas.pdf"
SCREENSHOTS = ROOT / "docs" / "screenshots"
PAGE_SIZE = (1240, 1754)
BG = "#f7f7f4"
INK = "#20231f"
MUTED = "#5f665c"
ACCENT = "#18765a"
LINE = "#cfd7cc"
LINK_BLUE = "#155fb8"
REPO_URL = "https://github.com/rubencorrob-sudo/generador-recetas-inventario"
PROD_URL = "https://54-236-36-56.sslip.io"
DOCS_URL = "https://54-236-36-56.sslip.io/docs"
DUCKDNS_URL = "https://recetasruben.duckdns.org"
TEAM_MEMBERS = [
    "Sean Paul Marquez Toro",
    "Reyner David Barbosa de la Rosa",
    "Ruben Andres Corro Blanco",
]
PDF_LINKS = []


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


F_TITLE = font(46, True)
F_H1 = font(32, True)
F_H2 = font(24, True)
F_BODY = font(21)
F_SMALL = font(17)
F_SMALL_BOLD = font(17, True)


def page() -> Image.Image:
    return Image.new("RGB", PAGE_SIZE, BG)


def text(draw: ImageDraw.ImageDraw, xy, value: str, fill=INK, fnt=F_BODY, width=88, gap=8):
    x, y = xy
    for line in value.splitlines():
        if not line:
            y += fnt.size
            continue
        for wrapped in wrap(line, width=width):
            draw.text((x, y), wrapped, fill=fill, font=fnt)
            y += fnt.size + gap
    return y


def rounded_box(draw, box, fill="#ffffff", outline=LINE, radius=14):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def draw_link(draw, page_index: int, x: int, y: int, label: str, url: str):
    value = f"{label}: {url}"
    draw.text((x, y), value, fill=LINK_BLUE, font=F_SMALL_BOLD)
    width = draw.textlength(value, font=F_SMALL_BOLD)
    PDF_LINKS.append((page_index, (x, y, x + width, y + F_SMALL_BOLD.size + 8), url))


def diagram_box(draw, xy, label, color="#ffffff"):
    x, y, w, h = xy
    rounded_box(draw, (x, y, x + w, y + h), fill=color, radius=12)
    tw = draw.textlength(label, font=F_SMALL_BOLD)
    draw.text((x + (w - tw) / 2, y + h / 2 - 10), label, fill=INK, font=F_SMALL_BOLD)


def arrow(draw, start, end):
    draw.line((start, end), fill=ACCENT, width=4)
    x, y = end
    draw.polygon([(x, y), (x - 13, y - 8), (x - 13, y + 8)], fill=ACCENT)


def page_architecture():
    img = page()
    draw = ImageDraw.Draw(img)
    draw.text((72, 70), "Generador de Recetas con Inventario", fill=INK, font=F_TITLE)
    draw.text((72, 130), "Informe tecnico de entrega", fill=ACCENT, font=F_H2)

    rounded_box(draw, (72, 190, 1168, 490), fill="#ffffff", radius=14)
    draw.text((96, 212), "Entregables principales", fill=INK, font=F_H2)
    draw_link(draw, 0, 96, 248, "Repositorio GitHub", REPO_URL)
    draw_link(draw, 0, 96, 278, "Aplicacion en produccion", PROD_URL)
    draw_link(draw, 0, 96, 308, "Documentacion Swagger", DOCS_URL)
    draw_link(draw, 0, 96, 338, "Dominio DuckDNS alterno", DUCKDNS_URL)
    draw.text((96, 380), "Integrantes", fill=INK, font=F_H2)
    member_y = 416
    for member in TEAM_MEMBERS:
        draw.text((112, member_y), f"- {member}", fill=INK, font=F_SMALL_BOLD)
        member_y += 28

    y = 540
    y = text(
        draw,
        (72, y),
        "Arquitectura monolitica modular con FastAPI. La interfaz tipo dashboard consume una API REST con JWT. El backend persiste usuarios, ingredientes, recetas enriquecidas y calificaciones en PostgreSQL, y encapsula OpenRouter en un servicio interno.",
        width=80,
    )

    diagram_y = y + 35
    diagram_box(draw, (95, diagram_y, 175, 75), "Usuario")
    diagram_box(draw, (315, diagram_y, 190, 75), "Navegador")
    diagram_box(draw, (555, diagram_y, 165, 75), "Caddy SSL", "#e4f4ee")
    diagram_box(draw, (770, diagram_y, 180, 75), "FastAPI", "#e4f4ee")
    diagram_box(draw, (1000, diagram_y, 160, 75), "Postgres")
    arrow(draw, (270, diagram_y + 38), (315, diagram_y + 38))
    arrow(draw, (505, diagram_y + 38), (555, diagram_y + 38))
    arrow(draw, (720, diagram_y + 38), (770, diagram_y + 38))
    arrow(draw, (950, diagram_y + 38), (1000, diagram_y + 38))
    diagram_box(draw, (770, diagram_y + 130, 180, 75), "OpenRouter")
    draw.line((860, diagram_y + 75, 860, diagram_y + 130), fill=ACCENT, width=4)

    y = diagram_y + 270
    draw.text((72, y), "Decisiones tecnicas", fill=INK, font=F_H1)
    y += 50
    bullets = [
        "JWT HS256 firmado con SECRET_KEY y contrasenas con PBKDF2 + sal unica.",
        "SQLAlchemy 2 permite PostgreSQL en produccion y SQLite temporal en pruebas.",
        "Motor local recomienda recetas con canasta familiar, compatibilidad y desglose.",
        "El prompt exige JSON valido con preferencias, nutricion estimada, consejos, faltantes y tags.",
        "El usuario no conversa libremente con el modelo: genera recetas desde inventario y opciones.",
        "Dashboard con score de inventario, favoritos, busqueda y copia de recetas.",
        "Docker Compose separa app, base de datos y proxy HTTPS con Caddy.",
    ]
    for item in bullets:
        y = text(draw, (90, y), f"- {item}", width=82)
        y += 5

    draw.text(
        (72, 1640),
        "Los enlaces de repositorio, produccion y Swagger estan en la primera pagina.",
        fill=MUTED,
        font=F_SMALL,
    )
    return img


def page_er():
    img = page()
    draw = ImageDraw.Draw(img)
    draw.text((72, 70), "Modelo de base de datos", fill=INK, font=F_TITLE)
    draw.text((72, 130), "4 tablas minimas requeridas + relaciones", fill=ACCENT, font=F_H2)

    boxes = {
        "users": (90, 250, 420, 260),
        "ingredients": (730, 250, 420, 260),
        "recipes": (90, 700, 420, 385),
        "ratings": (730, 700, 420, 290),
    }
    fields = {
        "users": ["id PK", "email UK", "full_name", "password_hash", "created_at"],
        "ingredients": ["id PK", "owner_id FK -> users.id", "name", "quantity", "unit", "notes"],
        "recipes": [
            "id PK",
            "owner_id FK -> users.id",
            "name, description, servings",
            "ingredients + steps JSON",
            "tips + nutrition + tags JSON",
            "difficulty, favorite, prompt",
        ],
        "ratings": ["id PK", "user_id FK -> users.id", "recipe_id FK -> recipes.id", "score 1..5", "comment"],
    }
    for name, (x, y, w, h) in boxes.items():
        rounded_box(draw, (x, y, x + w, y + h), fill="#ffffff", radius=16)
        draw.rectangle((x, y, x + w, y + 52), fill="#e4f4ee")
        draw.text((x + 20, y + 14), name, fill=ACCENT, font=F_H2)
        fy = y + 75
        for field in fields[name]:
            draw.text((x + 24, fy), field, fill=INK, font=F_BODY)
            fy += 34

    arrow(draw, (510, 380), (730, 380))
    arrow(draw, (300, 510), (300, 700))
    arrow(draw, (510, 860), (730, 840))
    draw.text((540, 345), "1:N", fill=ACCENT, font=F_SMALL_BOLD)
    draw.text((320, 600), "1:N", fill=ACCENT, font=F_SMALL_BOLD)
    draw.text((575, 805), "1:N", fill=ACCENT, font=F_SMALL_BOLD)

    y = 1130
    draw.text((72, y), "Endpoints clave", fill=INK, font=F_H1)
    y += 48
    endpoints = [
        "POST /api/auth/register, POST /api/auth/login, GET /api/auth/me",
        "GET/POST/PUT/DELETE /api/ingredients",
        "POST /api/recipes/generate con preferencias culinarias",
        "GET /api/recipes/recommendations con match y desglose",
        "GET /api/ingredients/summary para score y sugerencias",
        "GET/PATCH/DELETE /api/recipes y favoritos",
        "POST /api/recipes/{id}/ratings",
    ]
    for endpoint in endpoints:
        y = text(draw, (90, y), f"- {endpoint}", width=76)
        y += 4
    return img


def paste_screenshot(canvas, path, box):
    src = Image.open(path).convert("RGB")
    contained = ImageOps.contain(src, (box[2] - box[0], box[3] - box[1]))
    x = box[0] + ((box[2] - box[0]) - contained.width) // 2
    y = box[1] + ((box[3] - box[1]) - contained.height) // 2
    canvas.paste(contained, (x, y))
    ImageDraw.Draw(canvas).rounded_rectangle(box, radius=14, outline=LINE, width=2)


def page_screenshots():
    img = page()
    draw = ImageDraw.Draw(img)
    draw.text((72, 70), "Capturas del sistema funcionando", fill=INK, font=F_TITLE)
    draw.text((72, 130), "Registro, inventario, receta generada y Swagger", fill=ACCENT, font=F_H2)

    items = [
        ("Login / registro", SCREENSHOTS / "01-login.png", (70, 220, 585, 760)),
        ("Inventario", SCREENSHOTS / "02-inventario.png", (655, 220, 1170, 760)),
        ("Receta calificada", SCREENSHOTS / "03-receta-generada.png", (70, 900, 585, 1440)),
        ("OpenAPI / Swagger", SCREENSHOTS / "04-swagger.png", (655, 900, 1170, 1440)),
    ]
    for title, shot, box in items:
        draw.text((box[0], box[1] - 35), title, fill=INK, font=F_H2)
        paste_screenshot(img, shot, box)

    draw.text((72, 1628), "Pruebas: 14 tests pytest verdes. Favicon visible en /static/favicon.ico.", fill=MUTED, font=F_SMALL)
    return img


pages = [page_architecture(), page_er(), page_screenshots()]
OUT.parent.mkdir(parents=True, exist_ok=True)
pages[0].save(OUT, "PDF", resolution=150, save_all=True, append_images=pages[1:])
doc = fitz.open(OUT)
for page_index, rect, uri in PDF_LINKS:
    page = doc[page_index]
    sx = page.rect.width / PAGE_SIZE[0]
    sy = page.rect.height / PAGE_SIZE[1]
    x0, y0, x1, y1 = rect
    page.insert_link(
        {
            "kind": fitz.LINK_URI,
            "from": fitz.Rect(x0 * sx, y0 * sy, x1 * sx, y1 * sy),
            "uri": uri,
        }
    )
linked_out = OUT.with_suffix(".linked.pdf")
doc.save(linked_out, deflate=True)
doc.close()
linked_out.replace(OUT)
print(OUT)
