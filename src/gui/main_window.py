import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
from ..core.git_assistant import GitAssistant
from ..core.ai_analyzer import AIAnalyzer
from ..utils.logger import Logger

logger = Logger(__name__)

class MainWindow:
    def __init__(self, root, repo_path):
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
        self.status_text = tk.Text(parent, height=3, wrap=tk.WORD)
        self.status_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.status_text.insert('1.0', "准备开始分析代码变更...\n")

    def create_analysis_section(self, parent):
        # 创建Frame来容纳分析结果
        analysis_frame = ttk.Frame(parent)
        analysis_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建左侧树形结构
        tree_frame = ttk.Frame(analysis_frame)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # 创建Treeview，使用树形结构
        self.tree = ttk.Treeview(tree_frame, show='tree headings', height=20)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置树形结构的样式
        style = ttk.Style()
        style.configure('Treeview', rowheight=25)  # 增加行高
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'))  # 设置标题字体
        
        # 添加垂直滚动条
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 添加水平滚动条
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 创建右侧详细信息文本框
        detail_frame = ttk.LabelFrame(analysis_frame, text="详细信息", padding=(5, 5, 5, 5))
        detail_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # 创建详细信息文本框
        self.detail_text = tk.Text(detail_frame, wrap=tk.WORD, width=60, height=20,
                                 font=('Arial', 10))
        self.detail_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加滚动条
        detail_scrollbar = ttk.Scrollbar(detail_frame, orient=tk.VERTICAL, command=self.detail_text.yview)
        detail_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        # 配置权重
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.columnconfigure(1, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(0, weight=1)
        
        # 创建右键菜单
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="复制", command=self.copy_selected_item)
        self.context_menu.add_command(label="展开所有", command=lambda: self.expand_all(self.tree.focus()))
        self.context_menu.add_command(label="折叠所有", command=lambda: self.collapse_all(self.tree.focus()))
        
        # 绑定事件
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.toggle_item)
        self.tree.bind("<<TreeviewSelect>>", self.show_detail)
        
        # 为详细信息文本框添加右键菜单
        self.detail_menu = tk.Menu(self.detail_text, tearoff=0)
        self.detail_menu.add_command(label="复制", command=self.copy_detail)
        self.detail_menu.add_command(label="全选", command=self.select_all_detail)
        self.detail_text.bind("<Button-3>", self.show_detail_menu)

    def show_detail_menu(self, event):
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

    def show_detail(self, event):
        """在右侧文本框中显示选中项的详细信息"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        item = selected_items[0]
        text = self.tree.item(item)['text']
        
        # 清空并显示新内容
        self.detail_text.delete('1.0', tk.END)
        
        # 设置标签样式
        self.detail_text.tag_configure('header', font=('Arial', 11, 'bold'))
        self.detail_text.tag_configure('subheader', font=('Arial', 10, 'bold'))
        self.detail_text.tag_configure('content', font=('Arial', 10))
        self.detail_text.tag_configure('separator', font=('Arial', 10))
        
        # 获取完整路径
        path = []
        current = item
        while current:
            path.insert(0, self.tree.item(current)['text'])
            current = self.tree.parent(current)
        
        # 显示路径
        self.detail_text.insert(tk.END, "【路径】\n", 'header')
        self.detail_text.insert(tk.END, " → ".join(path) + "\n", 'content')
        self.detail_text.insert(tk.END, "\n" + "="*50 + "\n\n", 'separator')
        
        # 显示内容
        self.detail_text.insert(tk.END, "【内容】\n", 'header')
        self.detail_text.insert(tk.END, text + "\n", 'content')
        
        # 如果是叶子节点，显示完整上下文
        if not self.tree.get_children(item):
            full_context = self._get_full_context(item)
            if full_context:
                self.detail_text.insert(tk.END, "\n" + "="*50 + "\n\n", 'separator')
                self.detail_text.insert(tk.END, "【完整上下文】\n", 'header')
                self.detail_text.insert(tk.END, full_context, 'content')

    def _get_full_context(self, item):
        """获取选中项的完整上下文"""
        try:
            parent = self.tree.parent(item)
            if not parent:
                return None
            
            context = []
            parent_text = self.tree.item(parent)['text']
            # 移除可能存在的emoji前缀
            parent_text = self._remove_emoji(parent_text)
            context.append(f"■ 类别：{parent_text}")
            context.append("")  # 添加空行
            
            # 获取同级项
            siblings = self.tree.get_children(parent)
            for sibling in siblings:
                sibling_text = self.tree.item(sibling)['text']
                # 移除可能存在的emoji前缀
                sibling_text = self._remove_emoji(sibling_text)
                if sibling == item:
                    context.append(f"▶ {sibling_text}")
                else:
                    context.append(f"  {sibling_text}")
            
            return "\n".join(context)
        except Exception:
            return None

    def _remove_emoji(self, text):
        """移除文本开头的emoji字符"""
        emoji_pattern = r'^[^\w\s]+'
        import re
        return re.sub(emoji_pattern, '', text).strip()

    def create_progress_bar(self, parent):
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(parent, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 5))
        
    def create_commit_section(self, parent):
        ttk.Label(parent, text="提交信息:").grid(row=4, column=0, sticky=tk.W, pady=(10,0))
        self.commit_message = tk.Text(parent, height=5, wrap=tk.WORD)
        self.commit_message.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E))

    def create_buttons(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.commit_button = ttk.Button(button_frame, text="提交", command=self.do_commit)
        self.commit_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="取消", command=self.root.destroy).pack(side=tk.LEFT, padx=5)

    def configure_grid(self, frame):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=3)  # 让分析结果区域占更多空间
        frame.rowconfigure(5, weight=1)  # 让提交信息区域也可以伸缩

    def update_status(self, message):
        self.status_text.delete('1.0', tk.END)
        self.status_text.insert('1.0', message + "\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()

    def start_analysis(self):
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

    def show_analysis_result(self, results):
        # 清除现有的所有项
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加新的分析结果
        for result in results:
            try:
                file_path = result['file']
                suggestions = json.loads(result['suggestions']) if isinstance(result['suggestions'], str) else result['suggestions']
                
                # 创建文件节点，添加图标提示
                file_node = self.tree.insert('', tk.END, text=f"📄 {file_path}", open=True)
                
                # 添加各个分析类别
                self._add_category(file_node, suggestions, 'code_quality', '💻 代码质量')
                self._add_category(file_node, suggestions, 'security_issues', '🔒 安全问题')
                self._add_category(file_node, suggestions, 'performance', '⚡ 性能优化')
                self._add_category(file_node, suggestions, 'best_practices', '✨ 最佳实践')
                
            except Exception as e:
                logger.error(f"处理分析结果时出错: {str(e)}")
                error_node = self.tree.insert('', tk.END, text=f"❌ 错误: {file_path}")
                self.tree.insert(error_node, tk.END, text=str(result.get('suggestions', '解析失败')))

    def _add_category(self, parent, data, category, category_name):
        """添加分析类别及其内容到树形结构"""
        if category in data:
            category_data = data[category]
            category_node = self.tree.insert(parent, tk.END, text=category_name, open=True)
            
            if isinstance(category_data, dict):
                # 定义类别的中文映射
                category_map = {
                    'changes': '变更内容',
                    'issues': '发现的问题',
                    'improvements': '改进建议',
                    'vulnerabilities': '安全漏洞',
                    'warnings': '安全警告',
                    'recommendations': '改进建议',
                    'bottlenecks': '性能瓶颈',
                    'optimizations': '优化建议',
                    'suggestions': '其他建议',
                    'violations': '规范问题',
                    'examples': '示例'
                }
                
                for key, values in category_data.items():
                    if values:  # 只有当有内容时才添加
                        # 使用中文映射，如果没有映射则使用原始key
                        display_name = category_map.get(key, key)
                        sub_node = self.tree.insert(category_node, tk.END, text=display_name, open=True)
                        if isinstance(values, list):
                            for value in values:
                                self.tree.insert(sub_node, tk.END, text=value)
                        else:
                            self.tree.insert(sub_node, tk.END, text=str(values))
            elif isinstance(category_data, list):
                for item in category_data:
                    self.tree.insert(category_node, tk.END, text=item)
            else:
                self.tree.insert(category_node, tk.END, text=str(category_data))

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

    def show_context_menu(self, event):
        """显示右键菜单"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_selected_item(self):
        """复制选中项的内容"""
        item = self.tree.selection()[0]
        text = self.tree.item(item)['text']
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)

    def toggle_item(self, event):
        """双击切换展开/折叠状态"""
        item = self.tree.identify_row(event.y)
        if item:
            if self.tree.item(item, 'open'):
                self.tree.item(item, open=False)
            else:
                self.tree.item(item, open=True)

    def expand_all(self, item):
        """展开所有子项"""
        if not item:
            return
        self.tree.item(item, open=True)
        for child in self.tree.get_children(item):
            self.expand_all(child)

    def collapse_all(self, item):
        """折叠所有子项"""
        if not item:
            return
        for child in self.tree.get_children(item):
            self.collapse_all(child)
        self.tree.item(item, open=False) 