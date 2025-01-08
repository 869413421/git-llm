from git import Repo
import os
from ..utils.config import Config
from ..utils.logger import Logger

logger = Logger(__name__)

class GitAssistant:
    def __init__(self, repo_path='.'):
        self.repo = Repo(repo_path)
        self.git = self.repo.git
        self.config = Config()

    def get_modified_files(self):
        """
        获取所有修改的文件列表（排除被忽略的文件）

        Returns:
            list: 修改的文件列表
        """
        # 获取所有修改的文件
        unstaged = [item.a_path for item in self.repo.index.diff(None)]
        staged = [item.a_path for item in self.repo.index.diff('HEAD')]
        untracked = self.repo.untracked_files
        
        # 合并所有修改的文件并去重
        all_files = list(set(unstaged + staged + untracked))
        
        # 过滤掉被忽略的文件
        filtered_files = [f for f in all_files if not self.config.should_ignore(f)]
        
        if len(all_files) != len(filtered_files):
            logger.info(f"已忽略 {len(all_files) - len(filtered_files)} 个文件")
            logger.debug(f"被忽略的文件: {set(all_files) - set(filtered_files)}")
        
        return filtered_files

    def get_file_diff(self, file_path):
        """获取指定文件的修改内容

        Args:
            file_path (str): 文件路径

        Returns:
            str: 文件修改内容
        """
        try:
            if file_path in self.repo.untracked_files:
                with open(os.path.join(self.repo.working_dir, file_path), 'r', encoding='utf-8') as f:
                    return f"New file: {file_path}\n" + f.read()
            
            unstaged_diff = self.git.diff(file_path)
            staged_diff = self.git.diff('--cached', file_path)
            
            combined_diff = ""
            if staged_diff:
                combined_diff += f"Staged changes in {file_path}:\n{staged_diff}\n"
            if unstaged_diff:
                combined_diff += f"Unstaged changes in {file_path}:\n{unstaged_diff}\n"
            
            return combined_diff.strip()
        except Exception as e:
            return f"Error getting diff for {file_path}: {str(e)}"

    def commit_changes(self, commit_message):
        """
        提交更改

        Args:
            commit_message (str): 提交信息
        Returns:
            None
        """
        modified_files = self.get_modified_files()
        if not modified_files:
            raise Exception("没有要提交的更改")
        
        self.repo.index.add(modified_files)
        self.repo.index.commit(commit_message) 