"""图片票据解析：OCR 提取文字。

使用 RapidOCR（基于 ONNX Runtime，无需 PaddlePaddle，兼容 Python 3.14）。
中文识别效果好，CPU 友好。
"""
import logging
from pathlib import Path

logger = logging.getLogger("customs_ai")

_ocr_engine = None


def _get_ocr():
    """懒加载 RapidOCR 引擎。"""
    global _ocr_engine
    if _ocr_engine is not None:
        return _ocr_engine

    from rapidocr_onnxruntime import RapidOCR

    logger.info("正在初始化 RapidOCR (首次运行会下载模型约 15MB)...")
    _ocr_engine = RapidOCR()
    logger.info("RapidOCR 初始化完成")
    return _ocr_engine


def extract_text_from_image(image_path: str | Path) -> str:
    """从图片中提取文字。

    Args:
        image_path: 图片路径 (jpg/png/bmp)

    Returns:
        提取的文本内容
    """
    ocr = _get_ocr()

    result, _elapse = ocr(str(image_path))

    if not result:
        return ""

    lines = []
    for item in result:
        text = item[1]              # 文字内容
        try:
            confidence = float(item[2])  # 置信度（可能是 str 或 float）
        except (ValueError, TypeError):
            confidence = 0.0
        if confidence > 0.5:
            lines.append(text)

    return "\n".join(lines)


def parse_image_document(image_path: str | Path) -> dict:
    """完整解析一份图片文档。

    Returns:
        {"text": str, "image_path": str, "engine": "rapidocr"}
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")

    supported = {".jpg", ".jpeg", ".png", ".bmp"}
    if path.suffix.lower() not in supported:
        raise ValueError(f"不支持的图片格式: {path.suffix}，支持 {supported}")

    text = extract_text_from_image(path)

    return {
        "text": text,
        "image_path": str(path),
        "engine": "rapidocr",
        "char_count": len(text),
    }
