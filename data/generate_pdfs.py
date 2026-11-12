"""生成模拟报关单/发票 PDF 文件，用于文档解析测试。

用法：
    pip install reportlab
    python data/generate_pdfs.py
"""
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

DATA_DIR = Path(__file__).parent / "sample_documents"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 注册中文字体
FONT_PATHS = [
    ("SimSun", "C:/Windows/Fonts/simsun.ttc"),
    ("SimHei", "C:/Windows/Fonts/simhei.ttf"),
    ("MSYaHei", "C:/Windows/Fonts/msyh.ttc"),
]
font_registered = False
for name, path in FONT_PATHS:
    try:
        pdfmetrics.registerFont(TTFont(name, path))
        font_registered = True
        CN_FONT = name
        break
    except Exception:
        continue

if not font_registered:
    CN_FONT = "Helvetica"


def create_declaration_pdf():
    """生成进口报关单样本。"""
    output = DATA_DIR / "进口报关单_样例.pdf"
    doc = SimpleDocTemplate(str(output), pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CNTitle", parent=styles["Title"], fontName=CN_FONT, fontSize=16)
    normal_style = ParagraphStyle("CNNormal", parent=styles["Normal"], fontName=CN_FONT, fontSize=10)

    elements = [
        Paragraph("中华人民共和国海关进口货物报关单", title_style),
        Spacer(1, 5*mm),
        Paragraph("预录入编号：I202409150001　　海关编号：—", normal_style),
        Spacer(1, 3*mm),
    ]

    # 报关单表格
    table_data = [
        ["经营单位", "深圳市XX贸易有限公司", "收货单位", "深圳市YY电子科技有限公司"],
        ["合同协议号", "CT2024-0888", "贸易方式", "一般贸易"],
        ["成交方式", "CIF深圳", "起运国", "日本"],
        ["件数", "50", "毛重(kg)", "1250.5"],
        ["净重(kg)", "1100.0", "币制", "人民币"],
    ]
    t = Table(table_data, colWidths=[30*mm, 60*mm, 30*mm, 55*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), CN_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
        ("BACKGROUND", (2, 0), (2, -1), colors.lightgrey),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 3*mm))

    # 商品明细表
    item_data = [
        ["商品编号", "商品名称及规格型号", "数量及单位", "原产国", "单价", "总价"],
        ["8471300000", "便携式自动数据处理设备\nBrandX ModelPro 14寸/i7/16G/512G", "100台", "日本", "3500.00", "350000.00"],
    ]
    t2 = Table(item_data, colWidths=[25*mm, 65*mm, 20*mm, 15*mm, 25*mm, 25*mm])
    t2.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), CN_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph("税费征收情况：关税税率0%，增值税税率13%", normal_style))
    elements.append(Paragraph("备注：本报关单为教学演示用途", normal_style))

    doc.build(elements)
    print(f"✅ {output}")


def create_invoice_pdf():
    """生成商业发票样本（故意制造金额不一致）。"""
    output = DATA_DIR / "商业发票_样例.pdf"
    doc = SimpleDocTemplate(str(output), pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("CNTitle", parent=styles["Title"], fontName=CN_FONT, fontSize=16)
    normal_style = ParagraphStyle("CNNormal", parent=styles["Normal"], fontName=CN_FONT, fontSize=10)

    elements = [
        Paragraph("COMMERCIAL INVOICE / 商业发票", title_style),
        Spacer(1, 5*mm),
        Paragraph("Invoice No: INV-2024-0777", normal_style),
        Paragraph("Date: 2024-09-10", normal_style),
        Spacer(1, 3*mm),
        Paragraph("Seller: Tokyo Electronics Co., Ltd.", normal_style),
        Paragraph("Buyer: Shenzhen XX Trading Co., Ltd.", normal_style),
        Paragraph("Payment Terms: T/T 30 days", normal_style),
        Paragraph("Trade Terms: CIF Shenzhen", normal_style),
        Spacer(1, 5*mm),
    ]

    item_data = [
        ["No.", "Description", "HS Code", "Qty", "Unit Price(USD)", "Amount(USD)"],
        ["1", "Laptop Computer BrandX ModelPro\n14inch/i7/16GB/512GB SSD", "8471.30", "100pcs", "485.00", "48,500.00"],
    ]
    t = Table(item_data, colWidths=[10*mm, 65*mm, 25*mm, 20*mm, 30*mm, 25*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), CN_FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 5*mm))
    elements.append(Paragraph("Total Amount: USD 48,500.00", normal_style))
    elements.append(Paragraph("Country of Origin: Japan", normal_style))
    elements.append(Paragraph("", normal_style))
    elements.append(Paragraph("⚠️ 注意：此发票金额与报关单申报金额不一致（报关单报350000元 vs 发票48500美元≈35万）", 
                               ParagraphStyle("warn", parent=normal_style, textColor=colors.red)))

    doc.build(elements)
    print(f"✅ {output}")


def main():
    print("生成模拟单据 PDF...\n")
    create_declaration_pdf()
    create_invoice_pdf()
    print(f"\n所有文件已保存到: {DATA_DIR}")


if __name__ == "__main__":
    main()
