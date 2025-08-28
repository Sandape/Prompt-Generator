from fastapi import APIRouter, HTTPException, status, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import timedelta
from typing import Optional

from models import User, UserCreate, UserLogin, CaptchaResponse, Token
from auth import (
    authenticate_user, create_access_token, get_password_hash,
    generate_captcha, verify_captcha, ACCESS_TOKEN_EXPIRE_MINUTES
)
from storage import storage

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    captcha: str = Form(...),
    captcha_id: str = Form(...)
):
    """用户注册"""
    try:
        # 验证密码确认
        if password != confirm_password:
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "两次输入的密码不一致"
            })

        # 验证验证码
        if not verify_captcha(captcha_id, captcha):
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "验证码错误"
            })

        # 检查邮箱是否已存在
        if storage.get_user_by_email(email):
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "该邮箱已被注册"
            })

        # 检查用户名是否已存在
        if storage.get_user_by_username(username):
            return templates.TemplateResponse("register.html", {
                "request": request,
                "error": "该用户名已被使用"
            })

        # 创建用户
        password_hash = get_password_hash(password)
        user = User(
            email=email,
            username=username,
            password_hash=password_hash
        )
        storage.create_user(user)

        return RedirectResponse(url="/login?message=注册成功，请登录", status_code=302)

    except Exception as e:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": f"注册失败: {str(e)}"
        })

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    """用户登录"""
    try:
        # 认证用户
        user = authenticate_user(email, password)
        if not user:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "邮箱或密码错误"
            })

        # 获取客户端信息
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

        # 记录登录日志
        storage.log_login(email, user.username, client_ip, user_agent)

        # 创建访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        # 重定向到菜单页面
        response = RedirectResponse(url="/menu", status_code=302)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return response

    except Exception as e:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": f"登录失败: {str(e)}"
        })

@router.post("/logout")
async def logout():
    """用户登出"""
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response

@router.get("/captcha", response_model=CaptchaResponse)
async def get_captcha():
    """获取验证码"""
    captcha_id, captcha_image = generate_captcha()
    return CaptchaResponse(captcha_id=captcha_id, captcha_image=captcha_image)
