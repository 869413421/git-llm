import json
import openai
from ..utils.config import Config
from ..utils.logger import Logger

logger = Logger(__name__)

class AIAnalyzer:
    def __init__(self):
        logger.info("初始化 AI 分析器...")
        try:
            config = Config()
            openai.api_key = config.api_key
            openai.base_url = config.api_base
            logger.info("AI 分析器初始化完成")
        except Exception as e:
            logger.exception("AI 分析器初始化失败")
            raise

    def analyze_changes(self, file_path, diff_content):
        """分析文件变更并返回结构化的建议"""
        logger.info(f"开始分析文件: {file_path}")
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo-1106",  # 使用支持 JSON 模式的模型
                response_format={ "type": "json_object" },
                messages=[
                    {
                        "role": "system",
                        "content": """你是一个专业的代码审查助手，请用中文分析代码变更并提供结构化的JSON格式建议。
                        你的响应必须是一个JSON对象，包含以下字段：
                        {
                            "code_quality": {
                                "changes": ["代码变更的具体内容描述"],
                                "issues": ["发现的代码质量问题"],
                                "improvements": ["代码改进建议"]
                            },
                            "security_issues": {
                                "vulnerabilities": ["安全漏洞描述"],
                                "warnings": ["安全警告信息"],
                                "recommendations": ["安全改进建议"]
                            },
                            "performance": {
                                "bottlenecks": ["性能瓶颈描述"],
                                "optimizations": ["优化建议"],
                                "suggestions": ["其他性能改进建议"]
                            },
                            "best_practices": {
                                "violations": ["违反最佳实践的地方"],
                                "recommendations": ["最佳实践建议"],
                                "examples": ["改进示例"]
                            }
                        }
                        
                        请确保：
                        1. 返回的是有效的JSON格式
                        2. 所有内容必须使用中文
                        3. 每个数组至少包含一个项目
                        4. 如果某个方面没有问题，使用积极的评价，例如"代码结构清晰"、"未发现安全问题"等
                        5. 建议要具体且可操作
                        6. 描述要清晰易懂
                        """
                    },
                    {
                        "role": "user",
                        "content": f"文件: {file_path}\n差异内容:\n{diff_content}"
                    }
                ]
            )
            
            result = response.choices[0].message.content
            # 确保返回的是有效的JSON
            return json.loads(result)
            
        except Exception as e:
            logger.error(f"分析文件 {file_path} 时发生错误: {str(e)}")
            return {
                'error': str(e),
                'code_quality': {'error': '分析失败'},
                'security_issues': {'error': '分析失败'},
                'performance': {'error': '分析失败'},
                'best_practices': {'error': '分析失败'}
            }

    def generate_commit_message(self, diffs):
        """生成提交信息"""
        logger.info("开始生成提交信息")
        try:
            combined_diff = "\n\n".join(diffs)
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                response_format={ "type": "json_object" },
                messages=[
                    {
                        "role": "system",
                        "content": """你是一个Git提交信息生成助手。请用中文分析代码变更并生成简洁明了的提交信息，使用约定式提交格式。
                        返回的JSON格式如下：
                        {
                            "type": "feat|fix|docs|style|refactor|test|chore",
                            "scope": "变更影响的范围",
                            "description": "简短的中文变更描述",
                            "body": "详细的中文变更说明"
                        }
                        
                        type说明：
                        - feat: 新功能
                        - fix: 修复bug
                        - docs: 文档变更
                        - style: 代码格式调整
                        - refactor: 代码重构
                        - test: 测试相关
                        - chore: 其他修改
                        
                        注意：
                        1. description必须用中文简洁描述变更内容
                        2. body可以详细描述变更原因和影响
                        3. scope是可选的，如果有明确的影响范围再填写
                        """
                    },
                    {
                        "role": "user",
                        "content": f"代码变更内容:\n{combined_diff}"
                    }
                ]
            )
            
            result = json.loads(response.choices[0].message.content)
            # 构造约定式提交信息
            commit_message = f"{result['type']}"
            if result.get('scope'):
                commit_message += f"({result['scope']})"
            commit_message += f": {result['description']}"
            if result.get('body'):
                commit_message += f"\n\n{result['body']}"
                
            return commit_message
            
        except Exception as e:
            logger.error(f"生成提交信息时发生错误: {str(e)}")
            return f"error: {str(e)}" 