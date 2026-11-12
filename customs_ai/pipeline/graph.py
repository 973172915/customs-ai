"""LangGraph 主编排：知识问答 + 文档解析双引擎。"""
from langgraph.graph import END, StateGraph

from customs_ai.config import settings
from customs_ai.pipeline.nodes import (
    node_extract_fields,
    node_generate_answer,
    node_parse_document,
    node_retrieve,
)
from customs_ai.pipeline.observability import PipelineTrace
from customs_ai.pipeline.state import AgentState


def build_knowledge_graph():
    """知识问答工作流：检索 → 生成回答。"""
    g = StateGraph(AgentState)
    g.add_node("retrieve", node_retrieve)
    g.add_node("generate_answer", node_generate_answer)
    g.set_entry_point("retrieve")
    g.add_edge("retrieve", "generate_answer")
    g.add_edge("generate_answer", END)
    return g.compile()


def build_document_graph():
    """文档解析工作流：解析PDF → 提取字段 → 校验。"""
    g = StateGraph(AgentState)
    g.add_node("parse_document", node_parse_document)
    g.add_node("extract_fields", node_extract_fields)
    g.set_entry_point("parse_document")
    g.add_edge("parse_document", "extract_fields")
    g.add_edge("extract_fields", END)
    return g.compile()


knowledge_app = build_knowledge_graph()
document_app = build_document_graph()


def run_knowledge_qa(query: str, session_id: str | None = None) -> dict:
    """知识库问答入口。"""
    trace = PipelineTrace(source=query[:50])
    init_state: AgentState = {
        "user_query": query,
        "session_id": session_id or uuid.uuid4().hex[:8],
        "mode": "knowledge",
        "_trace": trace,
    }
    result = knowledge_app.invoke(init_state)
    trace.save(settings.output_dir / trace.job_id)

    return {
        "session_id": init_state["session_id"],
        "query": query,
        "answer": result.get("answer", ""),
        "citations": result.get("citations", []),
        "retrieved_count": len(result.get("retrieved_chunks", [])),
        "metrics": trace.summary(),
    }


def run_document_parse(file_path: str, session_id: str | None = None) -> dict:
    """文档解析入口。"""
    trace = PipelineTrace(source=file_path)
    init_state: AgentState = {
        "user_query": file_path,
        "session_id": session_id or uuid.uuid4().hex[:8],
        "mode": "document",
        "_trace": trace,
    }
    result = document_app.invoke(init_state)
    trace.save(settings.output_dir / trace.job_id)

    return {
        "session_id": init_state["session_id"],
        "file": file_path,
        "fields": result.get("extracted_fields", {}),
        "validation": result.get("validation_result", {}),
        "metrics": trace.summary(),
    }


import uuid  # noqa: E402


def export_mermaid() -> str:
    return knowledge_app.get_graph().draw_mermaid()
