from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, Depends, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import string
from PIL import Image, ImageDraw, ImageFont
import io
import base64

from models import User, UserCreate, TokenData
from storage import storage

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 验证码存储（内存中，生产环境建议使用Redis）
captcha_store = {}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)

def authenticate_user(email: str, password: str) -> Optional[User]:
    """认证用户"""
    user = storage.get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_token_from_request(request: Request):
    """从请求中获取token"""
    # 优先从cookie中获取token
    authorization = request.cookies.get("access_token")
    if authorization and authorization.startswith("Bearer "):
        return authorization[7:]  # Remove "Bearer " prefix

    # 如果没有cookie，尝试从Authorization header获取
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]  # Remove "Bearer " prefix

    return None

def verify_token(request: Request):
    """验证令牌"""
    token = get_token_from_request(request)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(email=email)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data

def get_current_user(request: Request):
    """获取当前用户（作为依赖使用）"""
    return verify_token(request)

def generate_captcha() -> tuple[str, str]:
    """生成验证码"""
    # 生成随机验证码文本
    length = 4
    chars = string.ascii_letters + string.digits
    captcha_text = ''.join(secrets.choice(chars) for _ in range(length))

    # 创建图片
    width, height = 120, 40
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    # 绘制随机干扰线
    for _ in range(5):
        x1 = secrets.randbelow(width)
        y1 = secrets.randbelow(height)
        x2 = secrets.randbelow(width)
        y2 = secrets.randbelow(height)
        draw.line([(x1, y1), (x2, y2)], fill='lightgray', width=1)

    # 绘制验证码文本
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # 每个字符随机位置和颜色
    for i, char in enumerate(captcha_text):
        x = 20 + i * 20 + secrets.randbelow(10)
        y = 10 + secrets.randbelow(10)
        color = (
            secrets.randbelow(100) + 50,  # 避免太暗
            secrets.randbelow(100) + 50,
            secrets.randbelow(100) + 100  # 偏蓝色
        )
        draw.text((x, y), char, fill=color, font=font)

    # 转换为base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    # 生成验证码ID并存储
    captcha_id = secrets.token_hex(16)
    captcha_store[captcha_id] = captcha_text.upper()

    return captcha_id, f"data:image/png;base64,{img_str}"

def verify_captcha(captcha_id: str, user_input: str) -> bool:
    """验证验证码"""
    if captcha_id not in captcha_store:
        return False

    stored_captcha = captcha_store[captcha_id]
    user_input = user_input.upper()

    # 删除已使用的验证码
    del captcha_store[captcha_id]

    return stored_captcha == user_input
