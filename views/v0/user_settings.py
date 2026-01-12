from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from settings import FRONTEND_DIRECTORY

templates = Jinja2Templates(directory=FRONTEND_DIRECTORY)
router = APIRouter(prefix="", tags=["html"])


@router.get("/settings", response_class=HTMLResponse)
async def user_settings_page(request: Request):
    """
    Render the user settings page.
    """
    return templates.TemplateResponse("user_settings.html", {"request": request})