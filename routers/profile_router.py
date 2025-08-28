from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import httpx
import json

from models import AIConfigCreate, AIConfigUpdate, AITestRequest, AITestResponse, ApiResponse
from auth import get_current_user
from storage import storage

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def get_profile(request: Request, token_data: dict = Depends(get_current_user)):
    """获取个人中心页面"""
    try:
        # 获取当前用户信息
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

        # 获取用户的AI配置
        ai_config = storage.get_ai_config_by_user_id(user.id)

        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user,
            "ai_config": ai_config
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/config")
async def save_ai_config(
    config_data: AIConfigCreate,
    token_data: dict = Depends(get_current_user)
):
    """保存AI配置"""
    try:
        # 获取当前用户信息
        user = storage.get_user_by_email(token_data.email)
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "用户不存在"}
            )

        # 检查是否已有配置，如果有则更新，否则创建
        existing_config = storage.get_ai_config_by_user_id(user.id)

        if existing_config:
            # 更新配置
            updated_config = storage.update_ai_config(user.id, AIConfigUpdate(**config_data.dict()))
            if updated_config:
                return JSONResponse(
                    content={"success": True, "message": "AI配置更新成功"}
                )
            else:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"success": False, "message": "更新配置失败"}
                )
        else:
            # 创建新配置
            try:
                new_config = storage.create_ai_config(user.id, config_data)
                return JSONResponse(
                    content={"success": True, "message": "AI配置保存成功"}
                )
            except ValueError as e:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"success": False, "message": str(e)}
                )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"保存配置失败: {str(e)}"}
        )

@router.post("/test", response_model=AITestResponse)
async def test_ai_connection(
    test_request: AITestRequest,
    token_data: dict = Depends(get_current_user)
):
    """测试AI连接"""
    try:
        # 获取当前用户信息
        user = storage.get_user_by_email(token_data.email)
        if not user:
            return AITestResponse(
                success=False,
                message="用户不存在",
                ai_response=None
            )

        # 获取用户的AI配置
        ai_config = storage.get_ai_config_by_user_id(user.id)
        if not ai_config:
            return AITestResponse(
                success=False,
                message="请先配置AI服务信息",
                ai_response=None
            )

        # 调用AI API进行测试
        async with httpx.AsyncClient(timeout=30.0) as client:
            headers = {
                "Authorization": f"Bearer {ai_config.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": ai_config.model_name,
                "messages": [
                    {"role": "user", "content": test_request.message}
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }

            try:
                response = await client.post(
                    ai_config.api_url,
                    headers=headers,
                    json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    # 提取AI回复内容
                    if "choices" in result and len(result["choices"]) > 0:
                        ai_response = result["choices"][0]["message"]["content"]
                        return AITestResponse(
                            success=True,
                            message="AI连接测试成功",
                            ai_response=ai_response
                        )
                    else:
                        return AITestResponse(
                            success=False,
                            message="AI响应格式异常",
                            ai_response=None
                        )
                else:
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        if "error" in error_json:
                            error_detail = error_json["error"].get("message", error_detail)
                    except:
                        pass

                    return AITestResponse(
                        success=False,
                        message=f"AI服务请求失败 ({response.status_code}): {error_detail}",
                        ai_response=None
                    )

            except httpx.TimeoutException:
                return AITestResponse(
                    success=False,
                    message="请求超时，请检查网络连接或API地址",
                    ai_response=None
                )
            except httpx.ConnectError:
                return AITestResponse(
                    success=False,
                    message="无法连接到AI服务，请检查API地址",
                    ai_response=None
                )
            except Exception as e:
                return AITestResponse(
                    success=False,
                    message=f"网络请求异常: {str(e)}",
                    ai_response=None
                )

    except Exception as e:
        return AITestResponse(
            success=False,
            message=f"测试过程中发生错误: {str(e)}",
            ai_response=None
        )

@router.delete("/config")
async def delete_ai_config(token_data: dict = Depends(get_current_user)):
    """删除AI配置"""
    try:
        # 获取当前用户信息
        user = storage.get_user_by_email(token_data.email)
        if not user:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "用户不存在"}
            )

        # 删除AI配置
        if storage.delete_ai_config(user.id):
            return JSONResponse(
                content={"success": True, "message": "AI配置删除成功"}
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"success": False, "message": "AI配置不存在"}
            )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"删除配置失败: {str(e)}"}
        )
