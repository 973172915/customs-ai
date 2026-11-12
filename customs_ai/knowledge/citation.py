"""引用溯源：确保 LLM 回答附带出处。"""
from customs_ai.knowledge.ingest import KnowledgeBase


def format_context_with_citations(results: list[dict]) -> str:
    """将检索结果格式化为带编号的上下文，供 LLM 引用。"""
    if not results:
        return "未找到相关法规依据。"

    parts = []
    for i, r in enumerate(results, 1):
        source_info = f"[{i}] 来源：{r.get('source', '未知')}"
        if r.get("doc_type"):
            source_info += f" | 类型：{r['doc_type']}"
        if r.get("hs_code"):
            source_info += f" | HS编码：{r['hs_code']}"
        parts.append(f"{source_info}\n内容：{r['text']}")

    return "\n\n".join(parts)


def extract_citations(answer: str, results: list[dict]) -> list[dict]:
    """从 LLM 回答中提取实际引用的来源。"""
    import re

    cited_indices = re.findall(r"\[(\d+)\]", answer)
    citations = []
    seen = set()
    for idx_str in cited_indices:
        idx = int(idx_str)
        if 1 <= idx <= len(results) and idx not in seen:
            r = results[idx - 1]
            citations.append({
                "index": idx,
                "source": r.get("source", ""),
                "doc_type": r.get("doc_type", ""),
                "hs_code": r.get("hs_code"),
            })
            seen.add(idx)

    return citations
