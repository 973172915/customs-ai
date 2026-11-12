# 内网部署说明

## 环境要求
- Python 3.10+
- Ollama + qwen2.5:7b（约 5GB 内存）
- 总内存建议 16GB+

## 离线安装步骤

### 1. 在有网的机器上准备
```bash
pip download -r requirements.txt -d ./wheels
ollama pull qwen2.5:7b
```

### 2. 拷贝到内网机器
- audit-agent 源码目录
- wheels/ 目录
- Ollama 模型目录 (~/.ollama/models)

### 3. 内网机器安装
```bash
python -m venv .venv
.venv\Scripts\activate
pip install --no-index --find-links=./wheels -r requirements.txt
```

### 4. 启动
```bash
ollama serve &
python run.py
```
