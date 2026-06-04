from fastapi import APIRouter, Request
from fastapi import Response
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings

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


@router.get("/favicon.ico", include_in_schema=False)
def favicon() -> FileResponse:
    return FileResponse("static/favicon.ico")
