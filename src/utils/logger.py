import logging
import sys
from pathlib import Path
from datetime import datetime

"""日志管理类，提供统一的日志记录功能。

此类封装了Python的logging模块，提供:
1. 文件日志记录（debug级别）
2. 控制台日志输出（info级别）
3. 统一的日志格式
"""
class Logger:
    def __init__(self, name='ai_git_assistant'):
        """初始化日志记录器。

        Args:
            name (str): 日志记录器名称，默认为'ai_git_assistant'
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 如果logger已经有处理器，不重复添加
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """设置日志处理器。
        
        配置两个处理器：
        1. FileHandler: 记录所有级别日志到文件
        2. StreamHandler: 在控制台输出INFO及以上级别日志
        """
        # 创建日志目录
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # 文件处理器 - 记录所有日志
        log_file = log_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器 - 只记录INFO及以上级别
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, msg, *args, **kwargs):
        """记录debug级别日志。

        Args:
            msg: 日志消息
            *args: 传递给logger.debug的位置参数
            **kwargs: 传递给logger.debug的关键字参数
        """
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """记录info级别日志。

        Args:
            msg: 日志消息
            *args: 传递给logger.info的位置参数
            **kwargs: 传递给logger.info的关键字参数
        """
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """记录warning级别日志。

        Args:
            msg: 日志消息
            *args: 传递给logger.warning的位置参数
            **kwargs: 传递给logger.warning的关键字参数
        """
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """记录error级别日志。

        Args:
            msg: 日志消息
            *args: 传递给logger.error的位置参数
            **kwargs: 传递给logger.error的关键字参数
        """
        self.logger.error(msg, *args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        """记录异常信息。

        Args:
            msg: 日志消息
            *args: 传递给logger.exception的位置参数
            exc_info (bool): 是否包含异常堆栈信息，默认为True
            **kwargs: 传递给logger.exception的关键字参数
        """
        self.logger.exception(msg, *args, exc_info=exc_info, **kwargs) 