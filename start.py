#!/usr/bin/env python3
"""
Prompt Generator 启动脚本
"""

import os
import sys
import subprocess

def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import fastapi
        import uvicorn
        import jinja2
        import pillow
        import passlib
        import python_jose
        print("✅ 所有依赖包已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def create_directories():
    """创建必要的目录"""
    directories = ["data", "logs", "static/css", "static/js", "static/images", "templates"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ 创建目录: {directory}")

def start_server():
    """启动服务器"""
    print("🚀 启动 Prompt Generator...")
    print("📱 访问地址: http://localhost:8000")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)

    try:
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    print("🎯 Prompt Generator 启动器")
    print("=" * 50)

    if not check_dependencies():
        sys.exit(1)

    create_directories()

    start_server()
