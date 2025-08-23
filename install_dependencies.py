#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖包安装脚本
自动检查和安装恐龙测量工具所需的依赖包
"""

import subprocess
import sys
import importlib

def check_package(package_name):
    """检查包是否已安装"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """安装包"""
    try:
        print(f"正在安装 {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✓ {package_name} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {package_name} 安装失败: {e}")
        return False

def main():
    print("=" * 50)
    print("恐龙测量工具依赖包检查")
    print("=" * 50)
    
    # 需要检查的包列表
    packages = [
        ("pandas", "pandas"),
        ("PIL", "pillow"),
        ("matplotlib", "matplotlib"),
        ("numpy", "numpy")
    ]
    
    missing_packages = []
    
    # 检查每个包
    for module_name, package_name in packages:
        if check_package(module_name):
            print(f"✓ {package_name} 已安装")
        else:
            print(f"✗ {package_name} 未安装")
            missing_packages.append(package_name)
    
    print()
    
    if missing_packages:
        print("需要安装以下包:")
        for package in missing_packages:
            print(f"  - {package}")
        
        print("\n开始安装...")
        success_count = 0
        
        for package in missing_packages:
            if install_package(package):
                success_count += 1
        
        print(f"\n安装完成: {success_count}/{len(missing_packages)} 个包安装成功")
        
        if success_count == len(missing_packages):
            print("\n🎉 所有依赖包安装成功！")
            print("现在可以运行恐龙测量工具了。")
        else:
            print("\n⚠️  部分包安装失败，请手动安装。")
    else:
        print("🎉 所有依赖包都已安装！")
    
    print("\n建议:")
    print("1. 运行 'python \"Dinosaur Measurement Simple.py\"' 启动简化版")
    print("2. 如果遇到OpenCV问题，使用简化版替代")
    print("3. 简化版使用PIL替代OpenCV，兼容性更好")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"脚本执行错误: {e}")
    
    input("\n按回车键退出...")
