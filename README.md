# Git-LLM

Git-LLM 是一个基于人工智能的 Git 助手工具，它能够帮助开发者更智能地管理代码变更和提交信息。通过集成 OpenAI 的 GPT 模型，该工具可以自动分析代码变更并生成高质量的提交信息。

[![GitHub stars](https://img.shields.io/github/stars/869413421/git-llm.svg?style=social&label=Stars)](https://github.com/869413421/git-llm)
[![GitHub forks](https://img.shields.io/github/forks/869413421/git-llm.svg?style=social&label=Fork)](https://github.com/869413421/git-llm/fork)
[![GitHub watchers](https://img.shields.io/github/watchers/869413421/git-llm.svg?style=social&label=Watch)](https://github.com/869413421/git-llm)
[![GitHub issues](https://img.shields.io/github/issues/869413421/git-llm.svg)](https://github.com/869413421/git-llm/issues)
[![GitHub license](https://img.shields.io/github/license/869413421/git-llm.svg)](https://github.com/869413421/git-llm/blob/master/LICENSE)

![Star History Chart](https://api.star-history.com/svg?repos=869413421/git-llm&type=Date)

## 功能特性

- 🔍 自动检测和分析代码变更
- 🤖 AI 驱动的代码审查建议
- ✨ 智能生成规范的提交信息
- 🎯 支持文件过滤和忽略配置
- 🖥️ 用户友好的图形界面
- 📊 结构化的分析结果展示
- 🔄 实时分析进度显示
- 📝 详细的代码审查报告

## 界面特点

- 📑 树形结构展示分析结果
- 🔍 详细信息实时预览
- 📋 支持复制和全选操作
- 🔄 展开/折叠节点功能
- 📊 进度条显示分析进度
- 💡 智能分类展示建议：
  - 代码质量分析
  - 安全问题检查
  - 性能优化建议
  - 最佳实践推荐

## 安装说明

1. 确保你的系统已安装 Python 3.9 或更高版本
2. 克隆项目到本地：
   ```bash
   git clone https://github.com/869413421/git-llm.git
   cd git-llm
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 配置环境变量：
   - 复制 `.env.example` 为 `.env`
   - 在 `.env` 文件中设置你的 OpenAI API 密钥和其他必要配置

## 使用方法

1. 直接运行（使用当前目录作为 Git 仓库）：
   ```bash
   python main.py
   ```

2. 指定 Git 仓库路径：
   ```bash
   python main.py /path/to/your/repo
   ```

3. 在图形界面中：
   - 实时查看分析进度
   - 浏览结构化的代码分析结果
   - 查看详细的建议内容
   - 复制或保存分析结果
   - 生成智能提交信息
   - 提交代码变更

## 分析结果说明

工具会对代码变更进行多维度分析：

1. 代码质量
   - 变更内容概述
   - 潜在问题识别
   - 改进建议

2. 安全问题
   - 安全漏洞检测
   - 安全警告提示
   - 安全改进建议

3. 性能优化
   - 性能瓶颈识别
   - 优化建议
   - 改进方案

4. 最佳实践
   - 规范符合度检查
   - 最佳实践建议
   - 改进示例

## 配置说明

你可以通过 `.env` 文件配置以下选项：
- `OPENAI_API_KEY`: OpenAI API 密钥
- `OPENAI_API_BASE`: OpenAI API 基础 URL（可选）

通过 `.aigitignore` 文件可以配置需要忽略的文件模式，类似于 `.gitignore`。

## 贡献指南

欢迎提交 Pull Request 或创建 Issue 来帮助改进这个项目。在提交代码前，请确保：
1. 代码符合项目的编码规范
2. 添加必要的测试用例
3. 更新相关文档

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件
