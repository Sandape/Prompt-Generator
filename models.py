from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    """用户模型"""
    id: Optional[int] = None
    email: EmailStr
    username: str
    password_hash: str
    created_at: Optional[datetime] = None
    is_active: bool = True

class UserCreate(BaseModel):
    """用户创建模型"""
    email: EmailStr
    username: str
    password: str
    captcha: str

class UserLogin(BaseModel):
    """用户登录模型"""
    email: EmailStr
    password: str

class LoginLog(BaseModel):
    """登录日志模型"""
    timestamp: datetime
    email: EmailStr
    username: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class CaptchaResponse(BaseModel):
    """验证码响应模型"""
    captcha_id: str
    captcha_image: str  # base64编码的图片

class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """令牌数据模型"""
    email: Optional[str] = None

class Project(BaseModel):
    """项目空间模型"""
    id: Optional[int] = None
    user_id: int
    name: str
    development_standard: str
    interface_example: str
    entity_example: str
    mapper_example: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ProjectCreate(BaseModel):
    """项目创建模型"""
    name: str
    development_standard: str
    interface_example: Optional[str] = ""
    entity_example: Optional[str] = ""
    mapper_example: Optional[str] = ""

class ProjectUpdate(BaseModel):
    """项目更新模型"""
    name: Optional[str] = None
    development_standard: Optional[str] = None
    interface_example: Optional[str] = None
    entity_example: Optional[str] = None
    mapper_example: Optional[str] = None

class TaskType(BaseModel):
    """任务类型模型"""
    id: str
    name: str
    description: str
    icon: str

class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool
    message: str
    data: Optional[dict] = None

class RequestParamField(BaseModel):
    """请求参数字段模型"""
    parameter: str
    source: str  # "request_param" 或 "request_body"
    description: str = ""

class ResponseField(BaseModel):
    """响应字段模型"""
    parameter: str
    description: str = ""

class InterfaceTaskRequest(BaseModel):
    """接口类任务请求模型"""
    interface_name: str
    interface_description: str
    business_logic_description: str
    interface_path: str
    request_params: List[str] = []
    request_body_example: str
    request_structure_table: List[RequestParamField] = []
    response_body_example: str
    response_structure_table: List[ResponseField] = []
    database_ddls: List[str] = []
    project_id: int

class InterfaceTaskResponse(BaseModel):
    """接口类任务响应模型"""
    success: bool
    message: str
    prompt_content: Optional[str] = None

class AIConfig(BaseModel):
    """AI配置模型"""
    id: Optional[int] = None
    user_id: int
    api_key: str
    api_url: str
    model_name: str = "gpt-3.5-turbo"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class AIConfigCreate(BaseModel):
    """AI配置创建模型"""
    api_key: str
    api_url: str
    model_name: str = "gpt-3.5-turbo"

class AIConfigUpdate(BaseModel):
    """AI配置更新模型"""
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    model_name: Optional[str] = None

class AITestRequest(BaseModel):
    """AI测试请求模型"""
    message: str = "你好"

class AITestResponse(BaseModel):
    """AI测试响应模型"""
    success: bool
    message: str
    ai_response: Optional[str] = None

class BugFixTaskRequest(BaseModel):
    """故障类任务请求模型"""
    bash_info: str
    project_id: int