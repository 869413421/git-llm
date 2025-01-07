import os
import sys
import subprocess
from pathlib import Path

class Installer:
    def __init__(self):
        self.platform = sys.platform
        
    def install(self):
        if self.platform == 'win32':
            self.install_windows()
        elif self.platform == 'darwin':
            self.install_macos()
        elif self.platform.startswith('linux'):
            self.install_linux()
        else:
            print(f"不支持的操作系统: {self.platform}")
            
    def install_windows(self):
        try:
            import winreg
            # 获取程序路径
            exe_path = os.path.abspath("AIGitCommit.exe")
            
            # 添加右键菜单
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"Directory\Background\shell\AIGitCommit") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "AI Git Commit")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, exe_path)
                
            with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, r"Directory\Background\shell\AIGitCommit\command") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, f'"{exe_path}" "%V"')
                
            print("Windows右键菜单安装成功！")
        except Exception as e:
            print(f"安装失败：{str(e)}")
            
    def install_macos(self):
        try:
            # 创建 Services 目录
            services_dir = os.path.expanduser("~/Library/Services")
            os.makedirs(services_dir, exist_ok=True)
            
            # 创建服务文件
            workflow_content = """
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>NSServices</key>
                <array>
                    <dict>
                        <key>NSMenuItem</key>
                        <dict>
                            <key>default</key>
                            <string>AI Git Commit</string>
                        </dict>
                        <key>NSMessage</key>
                        <string>runWorkflowAsService</string>
                    </dict>
                </array>
            </dict>
            </plist>
            """
            
            service_path = os.path.join(services_dir, "AIGitCommit.workflow")
            with open(service_path, "w") as f:
                f.write(workflow_content)
                
            print("macOS服务菜单安装成功！")
        except Exception as e:
            print(f"安装失败：{str(e)}")
            
    def install_linux(self):
        try:
            # 创建桌面操作文件
            action_content = """
            [Desktop Entry]
            Type=Action
            Name=AI Git Commit
            Icon=git
            Profiles=directory;
            
            [X-Action-Profile directory]
            MimeTypes=inode/directory;
            Exec=AIGitCommit %f
            """
            
            action_path = os.path.expanduser("~/.local/share/file-manager/actions/aigitcommit.desktop")
            os.makedirs(os.path.dirname(action_path), exist_ok=True)
            
            with open(action_path, "w") as f:
                f.write(action_content)
                
            print("Linux文件管理器操作安装成功！")
        except Exception as e:
            print(f"安装失败：{str(e)}")
            
    def uninstall(self):
        if self.platform == 'win32':
            self.uninstall_windows()
        elif self.platform == 'darwin':
            self.uninstall_macos()
        elif self.platform.startswith('linux'):
            self.uninstall_linux()
            
    def uninstall_windows(self):
        try:
            import winreg
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\Background\shell\AIGitCommit\command")
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"Directory\Background\shell\AIGitCommit")
            print("Windows右键菜单移除成功！")
        except Exception as e:
            print(f"移除失败：{str(e)}")
            
    def uninstall_macos(self):
        try:
            service_path = os.path.expanduser("~/Library/Services/AIGitCommit.workflow")
            if os.path.exists(service_path):
                os.remove(service_path)
            print("macOS服务菜单移除成功！")
        except Exception as e:
            print(f"移除失败：{str(e)}")
            
    def uninstall_linux(self):
        try:
            action_path = os.path.expanduser("~/.local/share/file-manager/actions/aigitcommit.desktop")
            if os.path.exists(action_path):
                os.remove(action_path)
            print("Linux文件管理器操作移除成功！")
        except Exception as e:
            print(f"移除失败：{str(e)}")

def main():
    installer = Installer()
    
    print("AI Git Commit 安装程序")
    print("=" * 50)
    print("1. 安装集成")
    print("2. 移除集成")
    print("3. 退出")
    
    while True:
        choice = input("\n请选择操作 (1-3): ").strip()
        
        if choice == "1":
            installer.install()
        elif choice == "2":
            installer.uninstall()
        elif choice == "3":
            break
        else:
            print("无效的选择，请重试。")
    
    input("\n按Enter键退出...")

if __name__ == "__main__":
    main() 