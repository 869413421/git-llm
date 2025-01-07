import os
from dotenv import load_dotenv
from pathlib import Path
from .logger import Logger

logger = Logger(__name__)

class Config:
    def __init__(self):
        logger.info("初始化配置...")
        self.project_root = self._find_project_root()
        self._load_env_config()
        self._load_ignore_patterns()

    def _load_env_config(self):
        """加载环境变量配置"""
        env_path = self.project_root / '.env'
        
        logger.debug(f"查找配置文件: {env_path}")
        if not env_path.exists():
            example_path = self.project_root / '.env.example'
            if example_path.exists():
                logger.error(f"未找到配置文件: {env_path}")
                raise ValueError(
                    "未找到 .env 文件！请复制 .env.example 并重命名为 .env，"
                    "然后设置你的 OpenAI API Key"
                )
            else:
                logger.error("未找到配置文件和示例文件")
                raise ValueError(
                    "未找到 .env 文件！请创建 .env 文件并设置 OPENAI_API_KEY=your-api-key"
                )

        load_dotenv(env_path, override=True)
        logger.info("已加载环境变量配置")
        
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        
        if not self.openai_api_key:
            logger.error("未找到 OPENAI_API_KEY")
            raise ValueError(
                "OPENAI_API_KEY 未在 .env 文件中设置！\n"
                "请在 .env 文件中添加：OPENAI_API_KEY=your-api-key"
            )
        logger.info(f"使用 API KEY： {self.api_key}")
        logger.info(f"使用 API Base URL: {self.openai_api_base}")

    def _load_ignore_patterns(self):
        """加载忽略文件配置"""
        self.ignore_patterns = set()
        ignore_file = self.project_root / '.aigitignore'

        # 如果不存在忽略文件，创建默认的
        if not ignore_file.exists():
            logger.info("创建默认的 .aigitignore 文件")
            self._create_default_ignore_file(ignore_file)

        # 读取忽略配置
        logger.debug("加载 .aigitignore 配置")
        with open(ignore_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    self.ignore_patterns.add(line)
        
        logger.debug(f"已加载忽略模式: {self.ignore_patterns}")

    def _create_default_ignore_file(self, ignore_file):
        """创建默认的忽略文件"""
        default_ignore = '''# IDE配置文件
.idea/
.vscode/
*.iml
*.iws
*.ipr

# 编译输出
__pycache__/
*.py[cod]
*$py.class
*.so
build/
dist/

# 虚拟环境
venv/
env/
.env/
.venv/

# 日志文件
logs/
*.log

# 系统文件
.DS_Store
Thumbs.db'''
        
        with open(ignore_file, 'w', encoding='utf-8') as f:
            f.write(default_ignore)

    def should_ignore(self, file_path):
        """检查文件是否应该被忽略"""
        from fnmatch import fnmatch
        
        # 转换为相对路径
        if isinstance(file_path, Path):
            file_path = str(file_path.relative_to(self.project_root))
        
        # 检查是否匹配任何忽略模式
        for pattern in self.ignore_patterns:
            if pattern.endswith('/'):
                # 目录模式
                if file_path.startswith(pattern) or file_path.startswith(pattern[:-1]):
                    return True
            elif fnmatch(file_path, pattern):
                return True
        return False

    def _find_project_root(self):
        """查找项目根目录（包含 main.py 的目录）"""
        current_dir = Path(os.getcwd())
        logger.debug(f"开始查找项目根目录，当前目录: {current_dir}")
        
        while current_dir != current_dir.parent:
            if (current_dir / 'main.py').exists():
                logger.debug(f"找到项目根目录: {current_dir}")
                return current_dir
            current_dir = current_dir.parent
        
        logger.warning(f"未找到 main.py，使用当前目录: {Path.cwd()}")
        return Path.cwd()

    @property
    def api_key(self):
        return self.openai_api_key

    @property
    def api_base(self):
        return self.openai_api_base 