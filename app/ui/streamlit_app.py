"""Streamlit 关务智能助手界面。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from customs_ai.config import settings
from customs_ai.pipeline.graph import export_mermaid, run_document_parse, run_knowledge_qa

st.set_page_config(page_title="CustomsAI", page_icon="🛃", layout="wide")
st.title("🛃 关务智能助手")
st.caption("海关法规知识库问答（带出处） · 报关单据解析 · 本地模型推理")

tab_ask, tab_parse, tab_logs, tab_arch = st.tabs(
    ["💬 法规问答", "📄 单据解析", "📋 操作日志", "📐 架构"]
)

# 侧边栏
with st.sidebar:
    st.header("⚙️ 配置")
    st.markdown(f"**模型**: `{settings.ollama_model}`")
    st.markdown(f"**Ollama**: `{settings.ollama_base_url}`")
    st.markdown(f"**Top-K**: {settings.top_k}")

    st.divider()
    st.markdown("**💡 示例问题：**")
    examples = [
        "HS编码8471.30对应什么商品？",
        "进口锂离子电池有什么监管条件？",
        "什么是HS编码？如何确定商品的归类？",
        "智能手表应该归入哪个HS编码？",
        "跨境电商和个人行邮的税收有什么区别？",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{hash(ex)}"):
            st.session_state["input_query"] = ex

# ─── Tab 1: 知识问答 ────────────────────────────────

with tab_ask:
    query = st.text_input(
        "输入你的问题：",
        value=st.session_state.get("input_query", ""),
        placeholder="例如：HS编码8471.30的监管条件是什么？",
    )
    go = st.button("🔍 查询", type="primary", use_container_width=True)

    if go and query.strip():
        with st.status("检索中...", expanded=True) as status:
            st.write("① 检索法规知识库...")
            try:
                result = run_knowledge_qa(query.strip())
            except Exception as e:
                status.update(label="失败", state="error")
                st.error(f"执行失败：{e}")
                st.stop()
            status.update(label="完成！", state="complete", expanded=False)

        # 回答
        st.subheader("📝 回答")
        st.markdown(result["answer"])

        # 引用来源
        if result.get("citations"):
            st.subheader("📚 引用来源")
            for c in result["citations"]:
                st.markdown(
                    f"**[{c['index']}]** {c['source']} | 类型: {c['doc_type']}"
                    + (f" | HS编码: {c['hs_code']}" if c.get("hs_code") else "")
                )

        # 指标
        col1, col2, col3 = st.columns(3)
        col1.metric("检索片段", result["retrieved_count"])
        col2.metric("引用数", len(result.get("citations", [])))
        col3.metric("耗时", f"{result['metrics']['total_ms']/1000:.1f}s")

# ─── Tab 2: 文档解析 ────────────────────────────────

with tab_parse:
    st.markdown("上传报关单、发票等 PDF 文件，自动提取关键字段并校验。")

    uploaded = st.file_uploader("选择 PDF 文件", type=["pdf"])

    if uploaded and st.button("📄 解析文档", type="primary"):
        save_dir = settings.output_dir / "uploads"
        save_dir.mkdir(parents=True, exist_ok=True)
        path = save_dir / uploaded.name
        with open(path, "wb") as f:
            f.write(uploaded.getvalue())

        with st.spinner("解析中..."):
            try:
                result = run_document_parse(str(path))
            except Exception as e:
                st.error(f"解析失败：{e}")
                st.stop()

        # 字段展示
        st.subheader("📋 提取字段")
        fields = result.get("fields", {})
        if fields and "error" not in fields:
            df = pd.DataFrame([fields])
            st.dataframe(df, use_container_width=True)
        else:
            st.error(fields.get("error", "未提取到字段"))

        # 校验结果
        validation = result.get("validation", {})
        st.subheader("✅ 校验结果")
        if validation.get("is_valid"):
            st.success("所有检查通过")
        else:
            for issue in validation.get("issues", []):
                st.warning(f"⚠️ {issue}")

        # 导出
        if fields and "error" not in fields:
            csv_data = pd.DataFrame([fields]).to_csv(index=False).encode("utf-8-sig")
            st.download_button("⬇️ 导出 CSV", csv_data, file_name="extracted_fields.csv")

# ─── Tab 3: 审计日志 ────────────────────────────────

with tab_logs:
    log_path = settings.audit_log_path
    if log_path.exists():
        lines = log_path.read_text(encoding="utf-8").strip().split("\n")
        entries = [json.loads(l) for l in lines[-50:]]
        st.dataframe(pd.DataFrame(entries), use_container_width=True)
    else:
        st.info("暂无日志")

# ─── Tab 4: 架构 ────────────────────────────────

with tab_arch:
    st.code(export_mermaid(), language="mermaid")
