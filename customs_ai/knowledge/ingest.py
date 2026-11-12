"""知识库入库：加载 JSONL 数据 → 切块 → 向量化 → 存入 FAISS。"""
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from customs_ai.config import settings


class KnowledgeBase:
    """关务知识库：支持向量检索 + 元数据过滤。"""

    def __init__(self):
        self.model: SentenceTransformer | None = None
        self.index: faiss.Index | None = None
        self.chunks: list[dict] = []
        self._build()

    def _load_data(self) -> list[dict]:
        """加载所有 processed JSONL 文件。"""
        all_chunks = []
        data_dir = settings.knowledge_data_dir

        # HS 编码
        hs_path = data_dir / "hs_codes.jsonl"
        if hs_path.exists():
            for line in hs_path.read_text(encoding="utf-8").strip().split("\n"):
                item = json.loads(line)
                text = f"HS编码{item['hs_code']}：{item['name']}。{item.get('description', '')} 关税税率{item.get('tariff_rate', '未知')}，增值税{item.get('vat_rate', '13%')}，监管条件{item.get('supervision', '无')}"
                all_chunks.append({
                    "text": text,
                    "source": "《进出口税则》",
                    "doc_type": "税则",
                    "hs_code": item["hs_code"],
                    **item,
                })

        # 归类决定
        ruling_path = data_dir / "classification_rulings.jsonl"
        if ruling_path.exists():
            for line in ruling_path.read_text(encoding="utf-8").strip().split("\n"):
                item = json.loads(line)
                text = f"归类决定[{item['ruling_id']}]：{item['product_name']}。{item['product_desc']} 归类结论：归入{item['hs_code']}。理由：{item['reasoning']} 法律依据：{item['legal_basis']}"
                all_chunks.append({
                    "text": text,
                    "source": item["source"],
                    "doc_type": "归类决定",
                    "ruling_id": item["ruling_id"],
                    **item,
                })

        # FAQ
        faq_path = data_dir / "faq.jsonl"
        if faq_path.exists():
            for line in faq_path.read_text(encoding="utf-8").strip().split("\n"):
                item = json.loads(line)
                text = f"问题：{item['question']}\n回答：{item['answer']}"
                all_chunks.append({
                    "text": text,
                    "source": item["source"],
                    "doc_type": "FAQ",
                    **item,
                })

        # 操作规范
        sop_path = data_dir / "sop_documents.jsonl"
        if sop_path.exists():
            for line in sop_path.read_text(encoding="utf-8").strip().split("\n"):
                item = json.loads(line)
                # 按 section 切分
                sections = item["content"].split("\n\n")
                for i, sec in enumerate(sections):
                    if len(sec.strip()) > 20:
                        all_chunks.append({
                            "text": f"[{item['title']}] {sec.strip()}",
                            "source": item["source"],
                            "doc_type": "操作规范",
                            "title": item["title"],
                        })

        return all_chunks

    def _build(self):
        """构建向量索引。"""
        print("正在构建知识库...")
        self.chunks = self._load_data()
        print(f"  加载 {len(self.chunks)} 个文档片段")

        if not self.chunks:
            raise RuntimeError(
                "知识库为空！请先运行: python data/generate_data.py"
            )

        # 加载 embedding 模型
        self.model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

        # 编码所有文本
        texts = [c["text"] for c in self.chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
        embeddings = np.array(embeddings).astype("float32")

        # 构建 FAISS 索引（内积 = 余弦相似度，因为已归一化）
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)

        print(f"  索引构建完成，维度={dim}")

    def search(self, query: str, top_k: int | None = None) -> list[dict]:
        """检索最相关的文档片段。"""
        if not self.index or not self.model:
            return []

        top_k = top_k or settings.top_k
        query_emb = self.model.encode([query], normalize_embeddings=True).astype("float32")
        scores, indices = self.index.search(query_emb, min(top_k, len(self.chunks)))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            chunk = self.chunks[idx].copy()
            chunk["score"] = float(score)
            results.append(chunk)

        return results
