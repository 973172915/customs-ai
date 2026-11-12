"""全局配置。"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"

    # 数据路径
    knowledge_data_dir: Path = BASE_DIR / "data" / "processed"
    output_dir: Path = BASE_DIR / "output"

    # 检索参数
    top_k: int = 5
    rerank_enabled: bool = False

    # 日志
    audit_log_path: Path = BASE_DIR / "logs" / "audit_log.jsonl"

    # Agent
    max_retries: int = 3


settings = Settings()
settings.output_dir.mkdir(parents=True, exist_ok=True)
settings.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
