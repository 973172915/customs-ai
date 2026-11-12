"""Agent 状态定义。"""
from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """关务助手共享状态。"""

    # 输入
    user_query: str
    session_id: str
    mode: str  # knowledge / document / workflow

    # 知识问答中间产物
    retrieved_chunks: list[dict]
    context_text: str
    answer: str
    citations: list[dict]

    # 文档解析中间产物
    document_text: str
    extracted_fields: dict
    validation_result: dict

    # 错误处理
    error: str
    retry_count: int

    # 内部
    _trace: Any
