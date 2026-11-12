"""字段映射与校验：从非结构化文本提取报关单字段。"""
import json
import re

from pydantic import BaseModel, Field, ValidationError

from customs_ai.config import settings


class DeclarationFields(BaseModel):
    """报关单关键字段 schema。"""
    经营单位: str = ""
    收货单位: str = ""
    合同协议号: str = ""
    贸易方式: str = "一般贸易"
    成交方式: str = ""
    起运国: str = ""
    原产国: str = ""
    商品名称: str = ""
    HS编码: str = ""
    规格型号: str = ""
    数量: float | None = None
    单位: str = "台"
    单价: float | None = None
    总价: float | None = None
    币制: str = "人民币"


def validate_hs_code(code: str) -> tuple[bool, str]:
    """校验 HS 编码格式。"""
    code = code.strip().replace(".", "").replace(" ", "")
    if not code:
        return False, "HS编码为空"
    if not code.isdigit():
        return False, "HS编码必须全为数字"
    if len(code) not in (6, 8, 10):
        return False, f"HS编码长度应为6/8/10位，当前{len(code)}位"
    return True, "格式正确"


def check_amount_consistency(qty: float | None, unit_price: float | None, total: float | None) -> dict:
    """检查金额一致性：数量 × 单价 ≈ 总价。"""
    if qty is None or unit_price is None or total is None:
        return {"consistent": None, "message": "缺少必要字段，无法校验"}

    expected = qty * unit_price
    diff = abs(expected - total)
    tolerance = max(total * 0.01, 0.01)  # 1% 容差

    if diff <= tolerance:
        return {"consistent": True, "message": "金额一致"}
    else:
        return {
            "consistent": False,
            "message": f"金额不一致：数量×单价={expected:.2f}，申报总价={total:.2f}，差额={diff:.2f}",
            "expected_total": round(expected, 2),
        }


def extract_fields_with_llm(text: str) -> dict:
    """用 LLM 从非结构化文本中提取报关单字段。"""
    import ollama

    client = ollama.Client(host=settings.ollama_base_url)

    prompt = f"""你是一名专业的报关单据解析专家。从以下文档内容中精确提取报关单字段。

## 关键规则
1. HS编码是10位数字（如8471300000），不是金额
2. 总价 = 数量 × 单价，通常是一个合理的商品交易金额
3. 单价是每件商品的价格，总价是全部数量的总金额
4. 注意区分表格的列，不要把一列的值填到另一列

## 文档内容
{text[:3000]}

## 输出要求
只输出合法 JSON，格式如下（找不到的字段填空字符串""或null）：
{{
  "经营单位": "公司名",
  "收货单位": "公司名",
  "合同协议号": "编号",
  "贸易方式": "如一般贸易",
  "成交方式": "如CIF/FOB",
  "起运国": "国家名",
  "原产国": "国家名",
  "商品名称": "商品描述",
  "HS编码": "10位数字编码",
  "规格型号": "型号规格",
  "数量": 数字,
  "单位": "台/件/个等",
  "单价": 每件价格(数字),
  "总价": 总金额(数字),
  "币制": "人民币/美元等"
}}"""

    resp = client.chat(
        model=settings.ollama_model,
        messages=[
            {"role": "system", "content": "你是报关单据解析专家。只输出合法 JSON。"},
            {"role": "user", "content": prompt},
        ],
        options={"temperature": 0.1},
    )

    raw = resp["message"]["content"].strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
        return DeclarationFields(**data).model_dump()
    except (json.JSONDecodeError, ValidationError) as e:
        return {"error": f"解析失败: {str(e)[:200]}"}


def full_validate(fields: dict) -> dict:
    """对提取的字段做完整校验。"""
    issues = []

    # HS编码校验
    hs = fields.get("HS编码", "")
    if hs:
        valid, msg = validate_hs_code(hs)
        if not valid:
            issues.append(f"HS编码错误: {msg}")

    # 金额一致性
    consistency = check_amount_consistency(
        fields.get("数量"),
        fields.get("单价"),
        fields.get("总价"),
    )
    if consistency.get("consistent") is False:
        issues.append(consistency["message"])

    # 必填字段检查
    required = ["经营单位", "商品名称", "HS编码"]
    for field in required:
        if not fields.get(field):
            issues.append(f"缺少必填字段: {field}")

    return {
        "issues": issues,
        "is_valid": len(issues) == 0,
        "amount_check": consistency,
    }
