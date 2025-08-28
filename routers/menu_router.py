from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def get_menu(request: Request, token_data: dict = Depends(get_current_user)):
    """获取菜单页面"""
    return templates.TemplateResponse("menu.html", {"request": request})
