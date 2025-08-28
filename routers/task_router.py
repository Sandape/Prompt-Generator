from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from auth import get_current_user
from storage import storage
from models import InterfaceTaskRequest, InterfaceTaskResponse, RequestParamField, ResponseField
import json
import httpx
from datetime import datetime
import logging
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/{project_id}/interface", response_class=HTMLResponse)
async def get_interface_task_form(project_id: int, request: Request, token_data: dict = Depends(get_current_user)):
    """获取接口类任务表单页面"""
    try:
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        project = storage.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        if project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此项目")

        return templates.TemplateResponse("interface_task_form.html", {
            "request": request,
            "project": project,
            "user": user
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{project_id}/mechanism", response_class=HTMLResponse)
async def get_mechanism_task_form(project_id: int, request: Request, token_data: dict = Depends(get_current_user)):
    """获取机制类任务表单页面"""
    try:
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        project = storage.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        if project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此项目")

        return templates.TemplateResponse("task_form.html", {
            "request": request,
            "project": project,
            "task_type": "mechanism",
            "task_name": "机制类任务",
            "task_description": "配置缓存、定时任务等机制类任务"
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{project_id}/integration", response_class=HTMLResponse)
async def get_integration_task_form(project_id: int, request: Request, token_data: dict = Depends(get_current_user)):
    """获取集成类任务表单页面"""
    try:
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        project = storage.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        if project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此项目")

        return templates.TemplateResponse("task_form.html", {
            "request": request,
            "project": project,
            "task_type": "integration",
            "task_name": "集成类任务",
            "task_description": "例如给项目集成ElasticSearch等中间件任务"
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{project_id}/fault", response_class=HTMLResponse)
async def get_fault_task_form(project_id: int, request: Request, token_data: dict = Depends(get_current_user)):
    """获取故障类任务表单页面"""
    try:
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        project = storage.get_project_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        if project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此项目")

        return templates.TemplateResponse("task_form.html", {
            "request": request,
            "project": project,
            "task_type": "fault",
            "task_name": "故障类任务",
            "task_description": "修复bug任务"
        })
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/generate-interface-prompt", response_model=InterfaceTaskResponse)
async def generate_interface_prompt(request: InterfaceTaskRequest, token_data: dict = Depends(get_current_user)):
    """生成接口类任务的Prompt"""
    try:
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        project = storage.get_project_by_id(request.project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        if project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此项目")

        # 生成Prompt内容
        prompt_content = generate_interface_prompt_content(request, user.username, project)

        return InterfaceTaskResponse(
            success=True,
            message="Prompt生成成功",
            prompt_content=prompt_content
        )

    except Exception as e:
        return InterfaceTaskResponse(
            success=False,
            message=f"生成Prompt失败: {str(e)}"
        )

def generate_interface_prompt_content(request: InterfaceTaskRequest, username: str, project) -> str:
    """生成接口类任务的Prompt内容"""

    # 获取当前日期
    current_date = datetime.now().strftime("%Y/%m/%d")

    # 构建请求报文结构表（扩展为六列）
    request_structure_md = ""
    if request.request_structure_table:
        request_structure_md = "| 参数字段 | 字段描述 |\n"
        request_structure_md += "|---------|---------|\n"
        for field in request.request_structure_table:
            request_structure_md += f"| {field.parameter} | {field.description} |\n"

    # 构建响应报文结构表（扩展为六列）
    response_structure_md = ""
    if request.response_structure_table:
        response_structure_md = "| 参数字段 | 字段描述 |\n"
        response_structure_md += "|---------|---------|\n"
        for field in request.response_structure_table:
            response_structure_md += f"| {field.parameter} | {field.description} |\n"

    # 构建关联数据库表DDL
    ddl_content = ""
    for ddl in request.database_ddls:
        ddl_content += f"```sql\n{ddl}\n```\n\n"

    # 构建请求参数列表
    request_params_md = ""
    if request.request_params:
        for param in request.request_params:
            request_params_md += f"- {param}\n"

    # 模板内容
    template = f"""- sinci: {current_date}
- author: {username}

# 核心任务

{request.interface_name}是一个{request.interface_description}的接口，请你按要求完成{request.interface_name}的开发，接口将存放至（待填充）。

# 业务逻辑

{request.business_logic_description}

# 要求

{project.development_standard}

# 接口API

## 接口路径

```http
{request.interface_path}
```

## 请求体结构

{request_structure_md}

## 请求体示例

{request_params_md}

```json
{request.request_body_example}
```

## 响应体结构

{response_structure_md}

## 响应体示例

```json
{request.response_body_example}
```

# 关联数据库信息

{ddl_content}"""



    return template

@router.post("/generate-ai-enhanced-prompt", response_model=InterfaceTaskResponse)
async def generate_ai_enhanced_prompt(request: InterfaceTaskRequest, token_data: dict = Depends(get_current_user)):
    """生成AI增强的接口类任务Prompt"""
    try:
        user = storage.get_user_by_email(token_data.email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在")

        project = storage.get_project_by_id(request.project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

        if project.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权访问此项目")

        # 获取用户的AI配置
        ai_config = storage.get_ai_config_by_user_id(user.id)
        if not ai_config:
            return InterfaceTaskResponse(
                success=False,
                message="请先配置AI服务信息",
                prompt_content=None
            )

        # 生成基础Prompt内容
        base_prompt = generate_interface_prompt_content(request, user.username, project)

        # 调用AI服务增强响应结构表
        enhanced_prompt = await enhance_prompt_with_ai(request, base_prompt, ai_config, user.username)

        # 调用AI服务生成业务逻辑描述
        enhanced_prompt = await enhance_business_logic_with_ai(request, enhanced_prompt, ai_config, user.username)

        return InterfaceTaskResponse(
            success=True,
            message="AI增强Prompt生成成功",
            prompt_content=enhanced_prompt
        )

    except Exception as e:
        return InterfaceTaskResponse(
            success=False,
            message=f"AI增强Prompt生成失败: {str(e)}"
        )

async def enhance_prompt_with_ai(request: InterfaceTaskRequest, base_prompt: str, ai_config, username: str) -> str:
    """使用AI增强Prompt中的响应结构表"""

    # 构建AI请求报文模板
    ai_request_template = f"""# 核心任务

你是一名Web应用开发领域的资深的需求分析师兼任技术架构师，我会提供给你：接口名称与描述、相关的表模型设计（通过分析DDL得出）、接口报文格式表（以markDown格式的表格给出），你会根据我提供的信息和要求进行综合分析，得出接口请求报文和响应报文中的各个字段与数据库表字段的可能关联关系，将你推断得到的关联关系，以含有字段名、主数据源、关联数据源、关联数据源关系描述四列的表格形式返回，只返回表格即可。

# 要求

1. 发挥你在Web应用开发领域的丰富经验，综合**包括但不限于**以下两个标准进行综合评估，逐行分析接口报文结构表，填充每个报文字段的对应关系：
   1. 能够从数据库表中的"_"连接符字段，简单转译成Java应用中驼峰结构参数名的数据，一定是相关的，例如user_id和userId一定是同一个字段；
   2. 面对不能通过上一条规则匹配数据源的数据，你需要综合分析接口名称和描述、请求报文结构和响应报文结构、数据库表字段含义，进行评估，匹配在请求报文和响应报文中有可能与数据库表字段存在隐形关联的数据。
2. 只返回接口参数结构表（指将请求报文参数和响应报文参数整合到一起组成的含有字段名、主数据源、关联数据源、关联数据源关系描述四列的表格）。

# 接口名称与描述
【interface_name】
【interface_description】
【business_logic_description】


# 相关表模型设计
【database_ddls】


# 接口报文格式表
请求报文表：
【request_structure_md】
响应报文表：
【response_structure_md】



"""

    # 构建请求报文结构表
    request_structure_md = ""
    if request.request_structure_table:
        request_structure_md = "| 参数字段 | 字段描述 | 主关联数据 | 关系描述 | 辅关联数据 | 关系描述 |\n"
        request_structure_md += "|---------|---------|-----------|----------|-----------|----------|\n"
        for field in request.request_structure_table:
            request_structure_md += f"| {field.parameter} | {field.description} |  |  |  |  |\n"

    # 构建响应报文结构表（原始的）
    original_response_structure_md = ""
    if request.response_structure_table:
        original_response_structure_md = "| 参数字段 | 字段描述 | 主关联数据 | 关系描述 | 辅关联数据 | 关系描述 |\n"
        original_response_structure_md += "|---------|---------|-----------|----------|-----------|----------|\n"
        for field in request.response_structure_table:
            original_response_structure_md += f"| {field.parameter} | {field.description} |  |  |  |  |\n"

    # 构建关联数据库表DDL
    database_ddls = ""
    for ddl in request.database_ddls:
        database_ddls += f"```sql\n{ddl}\n```\n\n"

    # 填充AI请求模板
    ai_request_content = ai_request_template.replace("【interface_name】", request.interface_name or "")
    ai_request_content = ai_request_content.replace("【interface_description】", request.interface_description or "")
    ai_request_content = ai_request_content.replace("【business_logic_description】", request.business_logic_description or "")
    ai_request_content = ai_request_content.replace("【database_ddls】", database_ddls)
    ai_request_content = ai_request_content.replace("【request_structure_md】", request_structure_md)
    ai_request_content = ai_request_content.replace("【response_structure_md】", original_response_structure_md)

    # 调用AI服务
    ai_response = await call_ai_service(ai_request_content, ai_config, username)

    # 记录AI调用日志
    log_ai_call(username, ai_config, ai_request_content, ai_response)

    # 如果AI调用成功，将AI答复拼装到最后面
    if ai_response and ai_response.strip():
        enhanced_prompt = base_prompt + "\n\n# 接口参数数据源\n" + ai_response.strip()
        return enhanced_prompt
    else:
        # 如果AI调用失败，返回原始prompt
        return base_prompt

async def call_ai_service(prompt: str, ai_config, username: str) -> str:
    """调用AI服务"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            headers = {
                "Authorization": f"Bearer {ai_config.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": ai_config.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }

            response = await client.post(
                ai_config.api_url,
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    ai_response = result["choices"][0]["message"]["content"]
                    return ai_response
                else:
                    print(f"AI响应格式异常: {result}")
                    return ""
            else:
                error_detail = response.text
                try:
                    error_json = response.json()
                    if "error" in error_json:
                        error_detail = error_json["error"].get("message", error_detail)
                except:
                    pass
                print(f"AI服务请求失败 ({response.status_code}): {error_detail}")
                return ""

    except httpx.TimeoutException:
        print("AI服务请求超时")
        return ""
    except httpx.RequestError as e:
        print(f"无法连接到AI服务: {str(e)}")
        return ""
    except Exception as e:
        print(f"AI调用异常: {str(e)}")
        return ""

async def enhance_business_logic_with_ai(request: InterfaceTaskRequest, current_prompt: str, ai_config, username: str) -> str:
    """使用AI增强业务逻辑描述"""

    # 构建AI请求报文模板
    ai_request_template = """# 核心任务

你是一名Web应用开发领域的资深的【需求分析师兼任技术架构师】，我会提供给你：接口信息、请求报文样例、响应报文样例，你会根据我提供的信息和要求进行综合分析，返回一份接口业务逻辑描述给我。

# 要求

1. 发挥你在Web应用开发领域的丰富经验，根据接口名称、请求报文、响应报文进行综合分析，推测同类接口在行业内主流的业务逻辑；
2. 只返回纯净的业务逻辑描述，不返回任何多余描述。


# 接口信息



# 请求报文样例



# 响应报文样例




"""

    # 构建请求报文结构表
    request_structure_md = ""
    if request.request_structure_table:
        request_structure_md = "| 参数字段 | 字段描述 | 主关联数据 | 关系描述 | 辅关联数据 | 关系描述 |\n"
        request_structure_md += "|---------|---------|-----------|----------|-----------|----------|\n"
        for field in request.request_structure_table:
            request_structure_md += f"| {field.parameter} | {field.description} |  |  |  |  |\n"

    # 构建响应报文结构表
    response_structure_md = ""
    if request.response_structure_table:
        response_structure_md = "| 参数字段 | 字段描述 | 主关联数据 | 关系描述 | 辅关联数据 | 关系描述 |\n"
        response_structure_md += "|---------|---------|-----------|----------|-----------|----------|\n"
        for field in request.response_structure_table:
            response_structure_md += f"| {field.parameter} | {field.description} |  |  |  |  |\n"

    # 构建请求参数列表
    request_params_md = ""
    if request.request_params:
        for param in request.request_params:
            request_params_md += f"- {param}\n"

    # 填充AI请求模板
    ai_request_content = ai_request_template.replace("# 接口信息\n\n\n\n", f"# 接口信息\n\n{request.interface_name}\n{request.interface_description}\n{request.business_logic_description}\n\n")
    ai_request_content = ai_request_content.replace("# 请求报文样例\n\n\n\n", f"# 请求报文样例\n\n{request_structure_md}\n\n```json\n{request.request_body_example}\n```\n\n")
    ai_request_content = ai_request_content.replace("# 响应报文样例\n\n\n", f"# 响应报文样例\n\n{response_structure_md}\n\n```json\n{request.response_body_example}\n```\n\n")

    # 调用AI服务
    ai_response = await call_ai_service(ai_request_content, ai_config, username)

    # 记录AI调用日志
    log_ai_call(username, ai_config, ai_request_content, ai_response)

    # 如果AI调用成功，将AI答复替换业务逻辑部分
    if ai_response and ai_response.strip():
        # 查找业务逻辑部分并替换
        import re

        # 使用正则表达式查找业务逻辑部分
        business_logic_pattern = r'# 业务逻辑\n\n[^\n]*\n'
        replacement = f'# 业务逻辑\n\n{ai_response.strip()}\n\n'

        if re.search(business_logic_pattern, current_prompt):
            enhanced_prompt = re.sub(business_logic_pattern, replacement, current_prompt, flags=re.MULTILINE)
            return enhanced_prompt
        else:
            # 如果没有找到业务逻辑部分，直接在核心任务后添加
            core_task_pattern = r'# 核心任务\n\n[^\n]*\n\n'
            replacement = f'# 核心任务\n\n{request.interface_name}是一个{request.interface_description}的接口，请你按要求完成{request.interface_name}的开发，接口将存放至（待填充）。\n\n# 业务逻辑\n\n{ai_response.strip()}\n\n'
            enhanced_prompt = re.sub(core_task_pattern, replacement, current_prompt, flags=re.MULTILINE | re.DOTALL)
            return enhanced_prompt
    else:
        # 如果AI调用失败，返回原始prompt
        return current_prompt

def log_ai_call(username: str, ai_config, request_body: str, response_body: str):
    """记录AI调用日志"""
    try:
        # 创建日志目录
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 记录到aiChat.log文件
        log_file = os.path.join(log_dir, "aiChat.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_entry = f"""
[{timestamp}]
用户名: {username}
AI配置信息:
  - API URL: {ai_config.api_url}
  - Model: {ai_config.model_name}
  - API Key: {ai_config.api_key[:10]}...{ai_config.api_key[-10:] if len(ai_config.api_key) > 20 else ai_config.api_key}

原生请求体:
{request_body}

原生响应体:
{response_body}

---
"""

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    except Exception as e:
        print(f"记录AI调用日志失败: {str(e)}")
