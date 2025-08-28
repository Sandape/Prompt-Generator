#!/usr/bin/env python3
"""
Prompt Generator 简单测试脚本
"""

import requests
import json
import time
from pathlib import Path

def test_server_connection():
    """测试服务器连接"""
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器连接正常")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到服务器: {e}")
        print("请确保服务器已启动 (python main.py 或 python start.py)")
        return False

def test_data_files():
    """测试数据文件"""
    data_files = ["data/users.json", "logs/login.log"]
    for file_path in data_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ 数据文件存在: {file_path}")
        else:
            print(f"⚠️  数据文件不存在: {file_path} (将在首次使用时创建)")

def test_static_files():
    """测试静态文件"""
    static_files = [
        "static/css/style.css",
        "static/js/main.js",
        "templates/login.html",
        "templates/register.html",
        "templates/menu.html"
    ]

    for file_path in static_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ 静态文件存在: {file_path}")
        else:
            print(f"❌ 静态文件缺失: {file_path}")

def main():
    """主测试函数"""
    print("🧪 Prompt Generator 测试")
    print("=" * 50)

    # 测试静态文件
    test_static_files()
    print()

    # 测试数据文件
    test_data_files()
    print()

    # 测试服务器连接
    if test_server_connection():
        print("🎉 应用运行正常！")
        print("📱 请在浏览器中访问: http://localhost:8000")
    else:
        print("💡 提示：请先启动服务器")
        print("   方法1: python main.py")
        print("   方法2: python start.py")

if __name__ == "__main__":
    main()
