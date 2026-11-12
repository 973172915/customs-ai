"""PDF 文档解析：提取文本和表格。"""
from pathlib import Path

import fitz  # PyMuPDF


def extract_text(pdf_path: str | Path) -> str:
    """提取 PDF 全文。"""
    doc = fitz.open(str(pdf_path))
    texts = []
    for page in doc:
        texts.append(page.get_text())
    doc.close()
    return "\n".join(texts)


def extract_tables(pdf_path: str | Path) -> list[list[list[str]]]:
    """提取 PDF 中的表格，返回嵌套列表。

    Returns:
        [page][table][row][cell]
    """
    doc = fitz.open(str(pdf_path))
    all_tables = []
    for page in doc:
        tabs = page.find_tables()
        for tab in tabs:
            all_tables.append(tab.extract())
    doc.close()
    return all_tables


def parse_document(pdf_path: str | Path) -> dict:
    """完整解析一份 PDF 文档。

    Returns:
        {"text": str, "tables": list, "page_count": int}
    """
    doc = fitz.open(str(pdf_path))
    text_parts = []
    tables = []

    for page in doc:
        text_parts.append(page.get_text())
        for tab in page.find_tables():
            tables.append(tab.extract())

    page_count = len(doc)
    doc.close()

    return {
        "text": "\n".join(text_parts),
        "tables": tables,
        "page_count": page_count,
    }
