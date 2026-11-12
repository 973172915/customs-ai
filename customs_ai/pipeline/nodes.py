"""各节点实现：知识问答 + 文档解析。"""
import json
import uuid
from datetime import datetime
from pathlib import Path

import ollama

from customs_ai.config import settings
from customs_ai.knowledge.citation import extract_citations, format_context_with_citations
from customs_ai.knowledge.ingest import KnowledgeBase
from customs_ai.parser.field_mapper import extract_fields_with_llm, full_validate
from customs_ai.parser.image_reader import parse_image_document
from customs_ai.parser.pdf_reader import parse_document
from customs_ai.pipeline.observability import PipelineTrace
from customs_ai.pipeline.state import AgentState

# 全局知识库单例
_kb: KnowledgeBase | None = None


def get_kb() -> KnowledgeBase:
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb


def _call_llm(system: str, user: str) -> str:
    client = ollama.Client(host=settings.ollama_base_url)
    resp = client.chat(
        model=settings.ollama_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        options={"temperature": 0.3},
    )
    return resp["message"]["content"].strip()


def _log_audit(state: AgentState, event: str, extra=None):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": state.get("session_id", ""),
        "event": event,
        "query": state.get("user_query", ""),
        **(extra or {}),
    }
    with open(settings.audit_log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ─── 知识问答节点 ────────────────────────────────

SYSTEM_PROMPT_QA = """你是一名海关关务专家。根据提供的法规依据回答用户问题。

规则：
1. 每个论点必须标注来源，格式为 [编号]，如"根据[1]..."
2. 如果没有找到相关依据，明确说"未找到相关规定"
3. 不编造条款号或法规名称
4. 回答简洁明了，突出关键信息
5. 如涉及具体HS编码，给出完整编码和商品名称
"""


def node_retrieve(state: AgentState) -> AgentState:
    """检索相关知识。"""
    trace: PipelineTrace = state["_trace"]
    with trace.step("retrieve") as step:
        kb = get_kb()
        results = kb.search(state["user_query"])
        context = format_context_with_citations(results)
        step.finish_ok({"chunks": len(results), "top_score": results[0]["score"] if results else 0.0})
    return {"retrieved_chunks": results, "context_text": context}


def node_generate_answer(state: AgentState) -> AgentState:
    """基于检索结果生成带出处的回答。"""
    trace: PipelineTrace = state["_trace"]
    with trace.step("generate_answer") as step:
        context = state["context_text"]
        answer = _call_llm(
            SYSTEM_PROMPT_QA,
            f"## 法规依据\n\n{context}\n\n## 用户问题\n{state['user_query']}\n\n请回答（记得标注来源编号）：",
        )
        citations = extract_citations(answer, state["retrieved_chunks"])
        step.finish_ok({"answer_len": len(answer), "citations": len(citations)})
    _log_audit(state, "knowledge_qa", {"citations": len(citations)})
    return {"answer": answer, "citations": citations}


# ─── 文档解析节点 ────────────────────────────────

def node_parse_document(state: AgentState) -> AgentState:
    """解析上传的文档（PDF 或图片）。"""
    trace: PipelineTrace = state["_trace"]
    doc_path = state.get("user_query", "")
    with trace.step("parse_document") as step:
        if not Path(doc_path).exists():
            raise FileNotFoundError(f"文件不存在: {doc_path}")

        suffix = Path(doc_path).suffix.lower()
        if suffix == ".pdf":
            parsed = parse_document(doc_path)
            text = parsed["text"]
            meta = {"pages": parsed["page_count"], "tables": len(parsed["tables"])}
        elif suffix in (".jpg", ".jpeg", ".png", ".bmp"):
            parsed = parse_image_document(doc_path)
            text = parsed["text"]
            meta = {"engine": "paddleocr", "chars": len(text)}
        else:
            raise ValueError(f"不支持的文件格式: {suffix}，支持 PDF 和图片")

        step.finish_ok(meta)
    return {"document_text": text}


def node_extract_fields(state: AgentState) -> AgentState:
    """从文档文本中提取结构化字段。"""
    trace: PipelineTrace = state["_trace"]
    with trace.step("extract_fields") as step:
        fields = extract_fields_with_llm(state["document_text"])
        if "error" in fields:
            step.finish_err(fields["error"])
            return {"extracted_fields": fields, "validation_result": {"is_valid": False, "issues": [fields["error"]]}}
        validation = full_validate(fields)
        step.finish_ok({"fields_found": sum(1 for v in fields.values() if v and v != ""), "valid": validation["is_valid"]})
    _log_audit(state, "document_parse", {"valid": validation["is_valid"], "issues": len(validation["issues"])})
    return {"extracted_fields": fields, "validation_result": validation}
