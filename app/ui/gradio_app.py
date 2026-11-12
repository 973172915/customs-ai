"""Gradio 界面：关务智能助手。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import gradio as gr
import pandas as pd

from customs_ai.config import settings
from customs_ai.pipeline.graph import export_mermaid, run_document_parse, run_knowledge_qa


# ─── 知识问答 ────────────────────────────────

def ask_question(query: str):
    if not query.strip():
        return "请输入问题", ""
    try:
        result = run_knowledge_qa(query.strip())
        answer = result["answer"]

        # 格式化引用
        citations_text = ""
        if result.get("citations"):
            citations_text = "📚 引用来源:\n"
            for c in result["citations"]:
                line = f"[{c['index']}] {c['source']} | {c['doc_type']}"
                if c.get("hs_code"):
                    line += f" | HS: {c['hs_code']}"
                citations_text += line + "\n"

        metrics = f"\n\n---\n⏱️ 耗时: {result['metrics']['total_ms']/1000:.1f}s | 检索片段: {result['retrieved_count']} | 引用: {len(result.get('citations', []))}"
        return answer + metrics, citations_text
    except Exception as e:
        return f"❌ 执行失败: {e}", ""


# ─── 文档解析 ────────────────────────────────

def parse_document(file):
    if file is None:
        return "请上传 PDF 文件", None
    try:
        result = run_document_parse(file.name)
        fields = result.get("fields", {})

        if "error" in fields:
            return f"❌ 解析失败: {fields['error']}", None

        # 格式化输出
        output_lines = ["## 📋 提取字段\n"]
        for k, v in fields.items():
            if v and v != "":
                output_lines.append(f"- **{k}**: {v}")

        # 校验结果
        validation = result.get("validation", {})
        if validation.get("is_valid"):
            output_lines.append("\n✅ **所有检查通过**")
        else:
            output_lines.append("\n### ⚠️ 校验问题:")
            for issue in validation.get("issues", []):
                output_lines.append(f"- {issue}")

        metrics = result.get("metrics", {})
        output_lines.append(f"\n---\n⏱️ 耗时: {metrics.get('total_ms', 0)/1000:.1f}s")

        # 转 DataFrame 供展示
        df = pd.DataFrame([fields]) if fields else None
        return "\n".join(output_lines), df
    except Exception as e:
        return f"❌ 解析失败: {e}", None


# ─── 构建界面 ────────────────────────────────

with gr.Blocks(title="CustomsAI · 关务智能助手") as demo:
    gr.Markdown("# 🛃 关务智能助手")
    gr.Markdown("海关法规知识库问答（带出处） · 报关单据自动解析 · 本地模型推理")

    with gr.Tab("💬 法规问答"):
        with gr.Row():
            with gr.Column(scale=2):
                query_input = gr.Textbox(
                    label="输入你的问题",
                    placeholder="例如：HS编码8471.30对应什么商品？监管条件是什么？",
                    lines=2,
                )
                ask_btn = gr.Button("🔍 查询", variant="primary")

                gr.Examples(
                    examples=[
                        "HS编码8471.30对应什么商品？",
                        "进口锂离子电池有什么监管条件？",
                        "什么是HS编码？如何确定商品的归类？",
                        "智能手表应该归入哪个HS编码？",
                        "跨境电商和个人行邮的税收有什么区别？",
                        "如何申请海关商品预裁定？",
                    ],
                    inputs=query_input,
                )

            with gr.Column(scale=3):
                answer_output = gr.Markdown(label="回答")
                citation_output = gr.Textbox(label="引用来源", lines=5, interactive=False)

        ask_btn.click(fn=ask_question, inputs=query_input, outputs=[answer_output, citation_output])

    with gr.Tab("📄 单据解析"):
        gr.Markdown("上传报关单、发票等文件（支持 PDF 和图片），自动提取关键字段并校验。")
        with gr.Row():
            with gr.Column():
                file_input = gr.File(label="上传文件", file_types=[".pdf", ".jpg", ".jpeg", ".png"])
                parse_btn = gr.Button("📄 解析文档", variant="primary")
            with gr.Column():
                parse_output = gr.Markdown(label="解析结果")

        table_output = gr.Dataframe(label="提取字段", interactive=False)

        parse_btn.click(fn=parse_document, inputs=file_input, outputs=[parse_output, table_output])

    with gr.Tab("📐 架构"):
        gr.Markdown("## 系统架构图")
        gr.Markdown("""
```
┌─────────────────────────────────────────────────────┐
│                   CustomsAI 关务智能助手              │
├─────────────────────────────────────────────────────┤
│                                                       │
│  ┌──────────── 接入层 ────────────┐                  │
│  │  Gradio UI    FastAPI API      │                  │
│  └───────────────────┬───────────┘                  │
│                      │                               │
│  ┌──────────── 编排层 (LangGraph) ────────────┐      │
│  │                                             │      │
│  │  知识问答: retrieve → generate_answer       │      │
│  │  文档解析: parse_document → extract_fields  │      │
│  │                                             │      │
│  └───────────────────┬─────────────────────────┘      │
│                      │                                │
│  ┌──────────── 能力层 ────────────────────────┐      │
│  │                                             │      │
│  │  ┌────────────────┐  ┌──────────────────┐  │      │
│  │  │ RAG 引擎        │  │ 文档解析引擎      │  │      │
│  │  │ · bge-small-zh │  │ · PyMuPDF (PDF)  │  │      │
│  │  │ · FAISS 检索   │  │ · RapidOCR (图片)│  │      │
│  │  │ · 引用溯源     │  │ · LLM 字段提取   │  │      │
│  │  └────────────────┘  │ · 规则校验       │  │      │
│  │                       └──────────────────┘  │      │
│  │  ┌──────────────────────────────────────┐  │      │
│  │  │ LLM: Ollama + qwen2.5:7b (本地CPU)   │  │      │
│  │  └──────────────────────────────────────┘  │      │
│  └─────────────────────────────────────────────┘      │
│                      │                                │
│  ┌──────────── 数据层 ────────────────────────┐      │
│  │  FAISS 索引  |  JSONL 结构化数据  |  审计日志 │      │
│  └─────────────────────────────────────────────┘      │
│                                                       │
└─────────────────────────────────────────────────────┘
        """)

        gr.Markdown("## 文档解析流程")
        gr.Markdown("""
```
上传文件 (PDF / JPG / PNG)
        │
        ├─ PDF → PyMuPDF 提取文字层
        └─ 图片 → RapidOCR (PP-OCRv4) 识别文字
                    ↓
              原始文本
                    ↓
        LLM 结构化提取 (qwen2.5:7b)
                    ↓
              JSON 字段
                    ↓
        规则校验（HS编码格式 / 金额一致性 / 必填字段）
                    ↓
              输出结果 + 告警
```
        """)

        gr.Markdown("## LangGraph 工作流 (Mermaid)")
        gr.Markdown("粘贴到 https://mermaid.live 预览")
        gr.Code(export_mermaid())

        gr.Markdown("## 技术栈")
        gr.Markdown("""
| 组件 | 技术 | 说明 |
|------|------|------|
| LLM | Ollama + qwen2.5:7b | 本地 CPU 推理，离线可用 |
| Embedding | bge-small-zh-v1.5 | 中文语义检索 |
| 向量库 | FAISS | 轻量内存级检索 |
| OCR | RapidOCR (PP-OCRv4) | 中文识别，CPU 友好 |
| PDF | PyMuPDF | 文字+表格提取 |
| 编排 | LangGraph | 状态机+条件路由 |
| 界面 | Gradio | AI Demo 交互 |
        """)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8501)
