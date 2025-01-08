import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
from ..core.git_assistant import GitAssistant
from ..core.ai_analyzer import AIAnalyzer
from ..utils.logger import Logger

logger = Logger(__name__)

"""主窗口类，提供AI Git Assistant的主要操作界面。

此类提供了一个图形界面，用于：
1. 显示代码变更分析结果
2. 展示提交信息建议
3. 执行Git提交操作
"""
class MainWindow:
    def __init__(self, root, repo_path):
        """初始化主窗口。

        Args:
            root: tkinter根窗口实例
            repo_path (str): Git仓库路径
            
        Raises:
            Exception: 初始化失败时抛出异常
        """
        logger.info(f"初始化主窗口，仓库路径: {repo_path}")
        self.root = root
        self.root.title("AI Git Commit Assistant")
        
        try:
            self.git_assistant = GitAssistant(repo_path)
            self.ai_analyzer = AIAnalyzer()
            self.setup_ui()
            logger.info("主窗口初始化完成")
        except Exception as e:
            logger.exception("主窗口初始化失败")
            raise

    def setup_ui(self):
        """设置用户界面布局。
        
        创建并布局所有UI组件，包括：
        - 状态显示区域
        - 进度条
        - 分析结果显示区域
        - 提交信息编辑区域
        - 操作按钮
        """
        # 设置窗口大小和位置
        self.root.geometry("1200x800")  # 增大默认窗口大小
        self.root.minsize(800, 600)     # 增大最小窗口大小
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # UI组件设置
        self.create_status_section(main_frame)
        self.create_progress_bar(main_frame)
        self.create_analysis_section(main_frame)
        self.create_commit_section(main_frame)
        self.create_buttons(main_frame)
        
        # 配置grid权重
        self.configure_grid(main_frame)
        
        # 开始分析
        self.start_analysis()

    def create_status_section(self, parent):
        """创建状态显示区域。
        
        Args:
            parent: 父级窗口组件
        """
        self.status_text = tk.Text(parent, height=3, wrap=tk.WORD)
        self.status_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.status_text.insert('1.0', "准备开始分析代码变更...\n")

    def create_analysis_section(self, parent):
        """创建代码分析结果显示区域。
        
        Args:
            parent: 父级窗口组件
        """
        # 创建Frame来容纳分析结果
        analysis_frame = ttk.Frame(parent)
        analysis_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建总结信息部分
        summary_frame = ttk.LabelFrame(analysis_frame, text="变更总结", padding=(5, 5, 5, 5))
        summary_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=(0, 5))
        
        self.summary_text = tk.Text(summary_frame, wrap=tk.WORD, height=12, font=('Arial', 10))
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        summary_scrollbar = ttk.Scrollbar(summary_frame, orient=tk.VERTICAL, command=self.summary_text.yview)
        summary_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.summary_text.configure(yscrollcommand=summary_scrollbar.set)
        
        # 创建文件列表和详情区域
        content_frame = ttk.Frame(analysis_frame)
        content_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 左侧文件列表
        list_frame = ttk.LabelFrame(content_frame, text="变更文件", padding=(5, 5, 5, 5))
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 2.5))
        
        self.file_list = tk.Listbox(list_frame, font=('Arial', 10), selectmode=tk.SINGLE)
        self.file_list.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_list.yview)
        list_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_list.configure(yscrollcommand=list_scrollbar.set)
        
        # 右侧详细信息
        detail_frame = ttk.LabelFrame(content_frame, text="文件详情", padding=(5, 5, 5, 5))
        detail_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(2.5, 5))
        
        self.detail_text = tk.Text(detail_frame, wrap=tk.WORD, width=60, font=('Arial', 10))
        self.detail_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        detail_scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        detail_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        # 配置权重
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.columnconfigure(1, weight=1)
        analysis_frame.rowconfigure(1, weight=1)
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=2)
        content_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        summary_frame.columnconfigure(0, weight=1)
        
        # 绑定事件
        self.file_list.bind('<<ListboxSelect>>', self.show_file_detail)
        
        # 为详细信息文本框添加右键菜单
        self.detail_menu = tk.Menu(self.detail_text, tearoff=0)
        self.detail_menu.add_command(label="复制", command=self.copy_detail)
        self.detail_menu.add_command(label="全选", command=self.select_all_detail)
        self.detail_text.bind("<Button-3>", self.show_detail_menu)

    def show_file_detail(self, event):
        """显示选中文件的详细信息"""
        selection = self.file_list.curselection()
        if not selection:
            return
        
        index = selection[0]
        display_text = self.file_list.get(index)
        
        # 从显示文本中提取文件路径（去除问题统计部分）
        file_path = display_text.split("  (")[0] if "  (" in display_text else display_text
        
        # 清空并显示新内容
        self.detail_text.delete('1.0', tk.END)
        
        # 设置标签样式
        self.detail_text.tag_configure('header', font=('Arial', 11, 'bold'))
        self.detail_text.tag_configure('subheader', font=('Arial', 10, 'bold'))
        self.detail_text.tag_configure('content', font=('Arial', 10))
        self.detail_text.tag_configure('severe', font=('Arial', 10, 'bold'), foreground='red')
        self.detail_text.tag_configure('warning', font=('Arial', 10), foreground='orange')
        self.detail_text.tag_configure('suggestion', font=('Arial', 10), foreground='blue')
        
        if file_path in self.analysis_data:
            data = self.analysis_data[file_path]
            
            # 显示文件路径
            self.detail_text.insert(tk.END, "【文件路径】\n", 'header')
            self.detail_text.insert(tk.END, f"{file_path}\n\n", 'content')
            
            # 显示分析结果
            severity_names = {
                'severe': '严重问题',
                'warning': '警告',
                'suggestion': '建议'
            }
            
            for severity, type_data in data.items():
                all_items = []
                for items in type_data.values():
                    all_items.extend(items)
                    
                if all_items:
                    self.detail_text.insert(tk.END, f"【{severity_names[severity]}】\n", 'subheader')
                    for item in all_items:
                        self.detail_text.insert(tk.END, f"• {item}\n", severity)
                    self.detail_text.insert(tk.END, "\n")

    def show_analysis_result(self, results):
        """显示代码分析结果。
        
        处理并展示AI分析器返回的分析结果，包括：
        - 文件变更统计
        - 代码质量问题
        - 安全问题
        - 改进建议
        
        Args:
            results (list): 分析结果列表，每个元素包含文件路径和分析建议
        """
        # 清除现有的所有项
        self.file_list.delete(0, tk.END)
        self.analysis_data = {}  # 存储分析数据
        
        # 统计信息
        stats_data = {
            'severe': {'security': 0, 'standard': 0},
            'warning': {'security': 0, 'standard': 0},
            'suggestion': {'security': 0, 'standard': 0}
        }
        
        # 收集所有变更信息
        all_changes = []
        
        # 处理每个文件的分析结果
        for result in results:
            try:
                file_path = result['file']
                suggestions = json.loads(result['suggestions']) if isinstance(result['suggestions'], str) else result['suggestions']
                
                # 将分析结果分类
                file_data = {
                    'severe': {'security': [], 'standard': []},
                    'warning': {'security': [], 'standard': []},
                    'suggestion': {'security': [], 'standard': []}
                }
                
                # 严重问题判断规则
                severe_keywords = [
                    '密码泄露', '凭证泄露', '系统崩溃', '严重漏洞', '注入攻击', 
                    'SQL注入', 'XSS攻击', '远程执行', '权限提升', '拒绝服务',
                    '未授权访问', '敏感信息泄露'
                ]
                
                # 收集变更信息
                if 'changes' in suggestions:
                    changes = suggestions['changes']
                    if isinstance(changes, dict):
                        for change_type, details in changes.items():
                            if isinstance(details, list):
                                all_changes.extend(f"[{file_path}] {item}" for item in details)
                            else:
                                all_changes.append(f"[{file_path}] {details}")
                    elif isinstance(changes, list):
                        all_changes.extend(f"[{file_path}] {item}" for item in changes)
                    elif isinstance(changes, str):
                        all_changes.append(f"[{file_path}] {changes}")
                
                # 处理各类分析结果
                for category, content in suggestions.items():
                    if not content or category == 'changes':
                        continue
                        
                    items = []
                    if isinstance(content, dict):
                        for _, values in content.items():
                            if isinstance(values, list):
                                items.extend(values)
                            else:
                                items.append(values)
                    elif isinstance(content, list):
                        items.extend(content)
                    else:
                        items.append(content)
                    
                    for item in items:
                        if not isinstance(item, str):
                            continue
                            
                        # 跳过"未发现问题"类的信息
                        if '未发现' in item or '没有发现' in item:
                            continue
                            
                        # 确定问题类型
                        issue_type = 'security' if category == 'security_issues' else 'standard'
                        
                        # 确定严重程度
                        severity = 'warning'  # 默认为警告级别
                        if any(keyword in item.lower() for keyword in severe_keywords):
                            severity = 'severe'
                        elif '建议' in item or '优化' in item or '改进' in item or category == 'best_practices':
                            severity = 'suggestion'
                        
                        # 添加到对应分类
                        prefix = '[安全]' if issue_type == 'security' else '[规范]'
                        file_data[severity][issue_type].append(f"{prefix} {item}")
                        stats_data[severity][issue_type] += 1
                
                # 存储分析数据
                self.analysis_data[file_path] = file_data
                
                # 计算该文件的问题统计
                file_issues = {
                    'severe': sum(len(issues) for issues in file_data['severe'].values()),
                    'warning': sum(len(issues) for issues in file_data['warning'].values()),
                    'suggestion': sum(len(issues) for issues in file_data['suggestion'].values())
                }
                
                # 构建文件列表显示文本
                display_text = file_path
                total_issues = sum(file_issues.values())
                if total_issues > 0:
                    issue_parts = []
                    if file_issues['severe'] > 0:
                        issue_parts.append(f"严重:{file_issues['severe']}")
                    if file_issues['warning'] > 0:
                        issue_parts.append(f"警告:{file_issues['warning']}")
                    if file_issues['suggestion'] > 0:
                        issue_parts.append(f"建议:{file_issues['suggestion']}")
                    display_text += f"  ({', '.join(issue_parts)})"
                
                # 添加到列表
                self.file_list.insert(tk.END, display_text)
                
            except Exception as e:
                logger.error(f"处理分析结果时出错: {str(e)}")
                self.file_list.insert(tk.END, f"错误: {file_path}")
                self.analysis_data[f"错误: {file_path}"] = {
                    'severe': {'security': [str(result.get('suggestions', '解析失败'))], 'standard': []}
                }
        
        # 生成变更总结
        summary = "【变更总结】\n\n"
        
        # 1. 总体变更范围
        summary += "变更范围：\n"
        summary += f"• 涉及文件数：{len(results)}个\n"
        if all_changes:
            unique_changes = list(set(all_changes))
            summary += f"• 变更操作数：{len(unique_changes)}处\n"
        summary += "\n"
        
        # 2. 主要变更内容
        if all_changes:
            summary += "主要变更：\n"
            # 对变更内容进行分类和整理
            file_changes = {}
            for change in all_changes:
                parts = change.split("] ", 1)
                if len(parts) == 2:
                    file_path = parts[0][1:]  # 移除开头的 '['
                    change_desc = parts[1]
                    if file_path not in file_changes:
                        file_changes[file_path] = []
                    file_changes[file_path].append(change_desc)
            
            # 显示每个文件的变更
            for file_path, changes in file_changes.items():
                summary += f"• {file_path}：\n"
                for change in changes[:3]:  # 每个文件最多显示3个变更
                    summary += f"    - {change}\n"
                if len(changes) > 3:
                    summary += f"    - ... 等{len(changes)}处变更\n"
            summary += "\n"
        
        # 3. 问题统计
        summary += "问题统计：\n"
        severity_names = {'severe': '严重问题', 'warning': '警告', 'suggestion': '建议'}
        type_names = {'security': '安全', 'standard': '规范'}
        
        total_issues = sum(sum(type_stats.values()) for type_stats in stats_data.values())
        if total_issues > 0:
            # 按类型统计
            security_issues = sum(stats['security'] for stats in stats_data.values())
            standard_issues = sum(stats['standard'] for stats in stats_data.values())
            
            if security_issues > 0:
                summary += f"• 安全相关：发现{security_issues}个问题\n"
            if standard_issues > 0:
                summary += f"• 规范相关：发现{standard_issues}个问题\n"
            
            # 按严重程度统计
            for severity, type_stats in stats_data.items():
                total = sum(type_stats.values())
                if total > 0:
                    severity_name = severity_names[severity]
                    summary += f"• {severity_name}：{total}个\n"
                    for issue_type, count in type_stats.items():
                        if count > 0:
                            summary += f"    - {type_names[issue_type]}：{count}个\n"
        else:
            summary += "• 未发现潜在问题\n"
        
        # 4. 影响分析
        summary += "\n影响分析：\n"
        if total_issues > 0:
            if security_issues > 0:
                summary += "• 存在安全相关问题，建议及时处理\n"
            if standard_issues > 0:
                summary += "• 存在代码规范问题，建议遵循最佳实践\n"
            
            # 根据问题严重程度给出建议
            if stats_data['severe']['security'] > 0:
                summary += "• ⚠️ 发现严重安全问题，强烈建议修复后再提交\n"
            elif stats_data['severe']['standard'] > 0:
                summary += "• ⚠️ 发现严重规范问题，建议仔细审查\n"
        else:
            summary += "• 代码变更符合规范，未发现潜在风险\n"
        
        # 更新总结文本
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.insert('1.0', summary)
        
        # 生成提交信息
        commit_message = self.generate_commit_message(all_changes, stats_data)
        self.commit_message.delete('1.0', tk.END)
        self.commit_message.insert('1.0', commit_message)

    def generate_commit_message(self, all_changes, stats_data):
        """生成Git提交信息"""
        message = ""
        
        # 1. 添加主要变更概述
        if all_changes:
            # 对变更内容进行分类和整理
            file_changes = {}
            for change in all_changes:
                parts = change.split("] ", 1)
                if len(parts) == 2:
                    file_path = parts[0][1:]
                    change_desc = parts[1]
                    if file_path not in file_changes:
                        file_changes[file_path] = []
                    file_changes[file_path].append(change_desc)
            
            # 生成变更描述
            for file_path, changes in file_changes.items():
                message += f"• {file_path}:\n"
                for change in changes[:3]:  # 每个文件最多显示3个变更
                    message += f"    - {change}\n"
                if len(changes) > 3:
                    message += f"    - ... 等{len(changes)}处变更\n"
            message += "\n"
        
        # 2. 添加问题统计
        total_issues = sum(sum(type_stats.values()) for type_stats in stats_data.values())
        if total_issues > 0:
            message += "问题统计：\n"
            for severity, type_stats in stats_data.items():
                total = sum(type_stats.values())
                if total > 0:
                    if severity == 'severe':
                        message += f"• 严重问题: {total}个\n"
                    elif severity == 'warning':
                        message += f"• 警告: {total}个\n"
                    elif severity == 'suggestion':
                        message += f"• 建议: {total}个\n"
        
        return message.strip()

    def create_progress_bar(self, parent):
        """创建进度条。
        
        Args:
            parent: 父级窗口组件
        """
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(parent, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 5))
        
    def create_commit_section(self, parent):
        """创建提交信息编辑区域。
        
        Args:
            parent: 父级窗口组件
        """
        ttk.Label(parent, text="提交信息:").grid(row=4, column=0, sticky=tk.W, pady=(10,0))
        self.commit_message = tk.Text(parent, height=5, wrap=tk.WORD)
        self.commit_message.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))

    def create_buttons(self, parent):
        """创建操作按钮。
        
        Args:
            parent: 父级窗口组件
        """
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.commit_button = ttk.Button(button_frame, text="提交", command=self.do_commit)
        self.commit_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="取消", command=self.root.destroy).pack(side=tk.LEFT, padx=5)

    def configure_grid(self, frame):
        """配置网格布局权重。
        
        Args:
            frame: 要配置的框架组件
        """
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=3)  # 让分析结果区域占更多空间
        frame.rowconfigure(5, weight=1)  # 让提交信息区域也可以伸缩

    def update_status(self, message):
        """更新状态显示信息。
        
        Args:
            message (str): 状态信息
        """
        self.status_text.delete('1.0', tk.END)
        self.status_text.insert('1.0', message + "\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()

    def start_analysis(self):
        """开始分析代码变更。
        
        在后台线程中执行以下操作：
        1. 获取变更文件列表
        2. 分析每个文件的变更
        3. 生成提交信息建议
        4. 更新UI显示结果
        """
        def analyze():
            try:
                logger.info("开始分析代码变更")
                self.progress_var.set(0)
                self.update_status("正在检测文件变更...")
                
                modified_files = self.git_assistant.get_modified_files()
                
                if not modified_files:
                    logger.info("没有检测到文件变更")
                    self.progress_var.set(100)
                    self.show_analysis_result([{
                        'file': 'No changes',
                        'suggestions': json.dumps({'message': '没有检测到任何文件更改。'}, ensure_ascii=False)
                    }])
                    return

                total_files = len(modified_files)
                logger.info(f"检测到 {total_files} 个变更文件")
                self.update_status(f"检测到 {total_files} 个文件需要分析")
                
                analysis_results = []
                diffs = []
                
                for index, file_path in enumerate(modified_files, 1):
                    progress = (index / (total_files + 1)) * 100  # +1 为最后的提交消息生成预留进度
                    self.progress_var.set(progress)
                    
                    self.update_status(f"正在分析文件 ({index}/{total_files}): {file_path}")
                    logger.debug(f"分析文件: {file_path}")
                    
                    diff_content = self.git_assistant.get_file_diff(file_path)
                    diffs.append(f"File: {file_path}\n{diff_content}")
                    
                    suggestions = self.ai_analyzer.analyze_changes(file_path, diff_content)
                    # 确保suggestions是JSON格式
                    if isinstance(suggestions, str):
                        try:
                            suggestions = json.loads(suggestions)
                        except json.JSONDecodeError:
                            suggestions = {'analysis': suggestions}
                    
                    analysis_results.append({
                        'file': file_path,
                        'suggestions': json.dumps(suggestions, ensure_ascii=False)
                    })

                self.update_status("正在生成提交信息...")
                self.show_analysis_result(analysis_results)
                
                logger.info("生成提交信息")
                commit_message = self.ai_analyzer.generate_commit_message(diffs)
                self.commit_message.delete('1.0', tk.END)
                self.commit_message.insert('1.0', commit_message)
                
                self.progress_var.set(100)
                self.update_status("分析完成！")
                
            except Exception as e:
                logger.exception("分析过程中发生错误")
                self.update_status(f"错误: {str(e)}")
                messagebox.showerror("错误", str(e))
                self.root.destroy()
        
        threading.Thread(target=analyze, daemon=True).start()

    def show_detail_menu(self, event):
        """显示详细信息的右键菜单。
        
        Args:
            event: 鼠标事件对象
        """
        """显示详细信息的右键菜单"""
        self.detail_menu.post(event.x_root, event.y_root)

    def copy_detail(self):
        """复制详细信息文本框中的内容"""
        try:
            selected_text = self.detail_text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            selected_text = self.detail_text.get('1.0', tk.END)
        if selected_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)

    def select_all_detail(self):
        """全选详细信息文本框中的内容"""
        self.detail_text.tag_add(tk.SEL, "1.0", tk.END)
        self.detail_text.mark_set(tk.INSERT, "1.0")
        self.detail_text.see(tk.INSERT)

    def do_commit(self):
        commit_message = self.commit_message.get('1.0', tk.END).strip()
        if not commit_message:
            messagebox.showwarning("警告", "提交信息不能为空！")
            return
        
        try:
            self.git_assistant.commit_changes(commit_message)
            messagebox.showinfo("成功", "变更已提交！")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("错误", f"提交失败：{str(e)}")

    def _on_link_click(self, event):
        """处理文件路径链接点击事件"""
        index = self.summary_text.index(f"@{event.x},{event.y}")
        tags = self.summary_text.tag_names(index)
        for tag in tags:
            if tag.startswith("file_"):
                file_path = tag[5:]  # 移除 "file_" 前缀
                # 在文件列表中查找并选中对应文件
                for i in range(self.file_list.size()):
                    display_text = self.file_list.get(i)
                    list_file_path = display_text.split("  (")[0] if "  (" in display_text else display_text
                    if list_file_path == file_path:
                        self.file_list.selection_clear(0, tk.END)
                        self.file_list.selection_set(i)
                        self.file_list.see(i)
                        # 触发文件详情显示
                        self.show_file_detail(None)
                        break
                break 