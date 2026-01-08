from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from settings import FRONTEND_DIRECTORY

templates = Jinja2Templates(directory=FRONTEND_DIRECTORY)
router = APIRouter(prefix="", tags=["html"])


@router.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    """
    Render the main (index) page.
    """
    return templates.TemplateResponse("index.html", {"request": request})
