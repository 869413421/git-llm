import os
import sys
import shutil
from pathlib import Path
import PyInstaller.__main__

def clean_build():
    """清理构建文件"""
    print("清理旧的构建文件...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # PyInstaller参数
    args = [
        'main.py',  # 主程序
        '--name=ai-git-assistant',  # 可执行文件名
        '--onefile',  # 打包成单个文件
        '--noconsole',  # 不显示控制台窗口
        '--add-data=.env.example;.',  # 添加配置文件模板
        '--add-data=.aigitignore;.',  # 添加忽略文件
        '--clean',  # 清理临时文件
    ]

    # Windows下使用分号，Unix系统使用冒号
    if sys.platform != 'win32':
        args[4] = '--add-data=.env.example:.'
        args[5] = '--add-data=.aigitignore:.'

    # 运行PyInstaller
    PyInstaller.__main__.run(args)

def copy_resources():
    """复制必要的资源文件"""
    print("复制资源文件...")
    dist_dir = Path('dist')
    
    # 确保目标目录存在
    if not dist_dir.exists():
        dist_dir.mkdir(parents=True)

    # 复制说明文件
    readme = Path('README.md')
    if readme.exists():
        shutil.copy2(readme, dist_dir / 'README.md')

def main():
    try:
        # 清理旧的构建文件
        clean_build()
        
        # 构建可执行文件
        build_executable()
        
        # 复制资源文件
        copy_resources()
        
        print("\n构建成功！")
        print("可执行文件位于 dist 目录中")
        
    except Exception as e:
        print(f"构建失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 