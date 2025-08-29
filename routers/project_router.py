from fastapi import APIRouter, HTTPException, status, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from auth import get_current_user
from storage import storage
from models import Project, ProjectCreate, ProjectUpdate, ApiResponse, User         

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def get_projects_page(request: Request, token_data: dict = Depends(get_current_user)):
    """获取项目选择页面"""
    try:
        # 获取当前用户信息
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        # 获取用户的项目列表
        projects = storage.get_projects_by_user_id(user.id)
        can_create = storage.can_create_project(user.id)

        return templates.TemplateResponse("projects.html", {
            "request": request,
            "projects": projects,
            "can_create": can_create,
            "max_projects": 5
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/create", response_class=HTMLResponse)
async def get_create_project_page(request: Request, token_data: dict = Depends(get_current_user)):
    """获取创建项目页面"""
    try:
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        can_create = storage.can_create_project(user.id)
        if not can_create:
            return RedirectResponse(url="/projects", status_code=302)

        return templates.TemplateResponse("project_form.html", {
            "request": request,
            "action": "create",
            "title": "新建项目空间"
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/create")
async def create_project(
    request: Request,
    name: str = Form(...),
    development_standard: str = Form(""),
    interface_example: str = Form(""),
    entity_example: str = Form(""),
    mapper_example: str = Form(""),
    token_data: dict = Depends(get_current_user)
):
    """创建新项目"""
    try:
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        project_data = ProjectCreate(
            name=name,
            development_standard=development_standard or "",
            interface_example=interface_example or "",
            entity_example=entity_example or "",
            mapper_example=mapper_example or ""
        )

        project = storage.create_project(user.id, project_data)
        return RedirectResponse(url="/projects", status_code=302)

    except ValueError as e:
        # 项目数量限制错误
        return templates.TemplateResponse("project_form.html", {
            "request": request,
            "action": "create",
            "title": "新建项目空间",
            "error": str(e),
            "form_data": {
                "name": name,
                "development_standard": development_standard,
                "interface_example": interface_example,
                "entity_example": entity_example,
                "mapper_example": mapper_example
            }
        })
    except Exception as e:
        return templates.TemplateResponse("project_form.html", {
            "request": request,
            "action": "create",
            "title": "新建项目空间",
            "error": f"创建项目失败: {str(e)}",
            "form_data": {
                "name": name,
                "development_standard": development_standard,
                "interface_example": interface_example,
                "entity_example": entity_example,
                "mapper_example": mapper_example
            }
        })

@router.get("/{project_id}/edit", response_class=HTMLResponse)
async def get_edit_project_page(project_id: int, request: Request, token_data: dict = Depends(get_current_user)):
    """获取编辑项目页面"""
    try:
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        project = storage.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        if project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此项目")

        return templates.TemplateResponse("project_form.html", {
            "request": request,
            "action": "edit",
            "title": "编辑项目空间",
            "project": project
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{project_id}/edit")
async def update_project(
    project_id: int,
    request: Request,
    name: str = Form(...),
    development_standard: str = Form(""),
    interface_example: str = Form(""),
    entity_example: str = Form(""),
    mapper_example: str = Form(""),
    token_data: dict = Depends(get_current_user)
):
    """更新项目信息"""
    try:
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        project = storage.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        if project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此项目")

        update_data = ProjectUpdate(
            name=name,
            development_standard=development_standard or "",
            interface_example=interface_example or "",
            entity_example=entity_example or "",
            mapper_example=mapper_example or ""
        )

        updated_project = storage.update_project(project_id, update_data)
        if not updated_project:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新项目失败")

        return RedirectResponse(url="/projects", status_code=302)

    except Exception as e:
        project = storage.get_project_by_id(project_id)
        return templates.TemplateResponse("project_form.html", {
            "request": request,
            "action": "edit",
            "title": "编辑项目空间",
            "project": project,
            "error": f"更新项目失败: {str(e)}",
            "form_data": {
                "name": name,
                "development_standard": development_standard,
                "interface_example": interface_example,
                "entity_example": entity_example,
                "mapper_example": mapper_example
            }
        })

@router.get("/{project_id}")
async def get_project_details(project_id: int, token_data: dict = Depends(get_current_user)):
    """获取项目详细信息（用于编辑）"""
    try:
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        project = storage.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        if project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此项目")

        # 返回项目信息（转换为字典格式）
        return {
            "id": project.id,
            "name": project.name,
            "development_standard": project.development_standard,
            "interface_example": project.interface_example,
            "entity_example": project.entity_example,
            "mapper_example": project.mapper_example,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "user_id": project.user_id
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{project_id}/delete")
async def delete_project(project_id: int, token_data: dict = Depends(get_current_user)):
    """删除项目"""
    try:
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        project = storage.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        if project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此项目")

        success = storage.delete_project(project_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="删除项目失败")

        return RedirectResponse(url="/projects", status_code=302)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{project_id}/tasks", response_class=HTMLResponse)
async def get_project_tasks(project_id: int, request: Request, token_data: dict = Depends(get_current_user)):
    """进入项目空间的任务类型选择页面"""
    try:
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        project = storage.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        if project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此项目")

        # 任务类型定义
        task_types = [
            {
                "id": "interface",
                "name": "接口类任务",
                "description": "以接口为维度的开发任务",
                "icon": "🔗"
            },
            {
                "id": "mechanism",
                "name": "机制类任务",
                "description": "配置缓存、定时任务等机制类任务",
                "icon": "⚙️"
            },
            {
                "id": "integration",
                "name": "集成类任务",
                "description": "集成中间件服务任务",
                "icon": "🔧"
            },
            {
                "id": "fault",
                "name": "故障类任务",
                "description": "通过报错信息结合项目规范快速修复BUG",
                "icon": "🐛"
            }
        ]

        return templates.TemplateResponse("task_types.html", {
            "request": request,
            "project": project,
            "task_types": task_types
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
