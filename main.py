from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import datetime

from routers.auth_router import router as auth_router
from routers.menu_router import router as menu_router
from routers.project_router import router as project_router
from routers.task_router import router as task_router
from routers.profile_router import router as profile_router

# 创建应用
app = FastAPI(title="Prompt Generator", description="A FastAPI app for generating prompts")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 配置模板
templates = Jinja2Templates(directory="templates")

# 包含路由
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(menu_router, prefix="/menu", tags=["menu"])
app.include_router(project_router, prefix="/projects", tags=["projects"])
app.include_router(task_router, prefix="/tasks", tags=["tasks"])
app.include_router(profile_router, prefix="/profile", tags=["profile"])

@app.get("/", response_class=HTMLResponse)
async def root():
    """根路径重定向到登录页面"""
    return RedirectResponse(url="/login", status_code=302)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页面"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """注册页面"""
    return templates.TemplateResponse("register.html", {"request": request})



@app.get("/batch-translate", response_class=HTMLResponse)
async def batch_translate_page(request: Request):
    """批量转译页面（未开发完成）"""
    return templates.TemplateResponse("not_implemented.html", {
        "request": request,
        "feature": "批量转译"
    })

@app.get("/single-translate", response_class=HTMLResponse)
async def single_translate_page():
    """单次精译页面重定向到项目管理"""
    return RedirectResponse(url="/projects", status_code=302)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=4397, reload=True)
