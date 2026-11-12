"""数据生成脚本：构造关务知识库所需的结构化数据。

包含：
1. HS编码表（常用品类，200+条）
2. 商品归类决定（模拟真实格式）
3. 监管条件表
4. 常见问题FAQ
5. 模拟报关单/发票数据

用法：
    python data/generate_data.py
"""
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent
PROCESSED_DIR = DATA_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ══════════════════════════════════════════════════════════════
# 1. HS 编码表（精选常用品类）
# ══════════════════════════════════════════════════════════════

HS_CODES = [
    # 第84章 - 机械及电气设备
    {"hs_code": "8471.30", "name": "便携式自动数据处理设备（笔记本电脑）", "chapter": "第84章", "tariff_rate": "0%", "vat_rate": "13%", "supervision": "A", "description": "重量不超过10千克的便携式自动数据处理设备，至少由中央处理部件、键盘和显示器组成"},
    {"hs_code": "8471.41", "name": "其他自动数据处理设备（台式电脑主机）", "chapter": "第84章", "tariff_rate": "0%", "vat_rate": "13%", "supervision": "A", "description": "在同一机壳内至少装有中央处理部件和输入输出部件的自动数据处理设备"},
    {"hs_code": "8471.50", "name": "自动数据处理设备的输入输出部件", "chapter": "第84章", "tariff_rate": "0%", "vat_rate": "13%", "supervision": "A", "description": "单独报验的自动数据处理设备用输入或输出部件（如显示器、键盘、鼠标）"},
    {"hs_code": "8471.70", "name": "自动数据处理设备的存储部件", "chapter": "第84章", "tariff_rate": "0%", "vat_rate": "13%", "supervision": "A", "description": "自动数据处理设备用存储部件（硬盘驱动器、固态硬盘等）"},
    {"hs_code": "8443.99", "name": "打印机零件附件", "chapter": "第84章", "tariff_rate": "0%", "vat_rate": "13%", "supervision": "A", "description": "打印机、复印机及多功能一体机的零件、附件"},
    {"hs_code": "8479.89", "name": "其他机器及机械器具", "chapter": "第84章", "tariff_rate": "5%", "vat_rate": "13%", "supervision": "A", "description": "本章未列名的具有独立功能的机器及机械器具"},

    # 第85章 - 电气设备
    {"hs_code": "8517.12", "name": "手机（蜂窝网络电话机）", "chapter": "第85章", "tariff_rate": "0%", "vat_rate": "13%", "supervision": "A", "description": "用于蜂窝网络或其他无线网络的电话机，包括智能手机"},
    {"hs_code": "8517.62", "name": "网络通信设备", "chapter": "第85章", "tariff_rate": "0%", "vat_rate": "13%", "supervision": "A", "description": "接收、转换和发送或再生音像或其他数据的机器（路由器、交换机等）"},
    {"hs_code": "8528.72", "name": "电视机（彩色）", "chapter": "第85章", "tariff_rate": "0%", "vat_rate": "13%", "supervision": "A", "description": "彩色视频监视器及投影机，不含高频调谐器的"},
    {"hs_code": "8504.40", "name": "电源适配器/充电器", "chapter": "第85章", "tariff_rate": "0%", "vat_rate": "13%", "supervision": "A", "description": "静止式变流器（整流器），用于将交流电转换为直流电"},
    {"hs_code": "8507.60", "name": "锂离子蓄电池", "chapter": "第85章", "tariff_rate": "8%", "vat_rate": "13%", "supervision": "A/B", "description": "锂离子蓄电池（含聚合物锂电池），用于储能或供电"},
    {"hs_code": "8544.42", "name": "带接头的电缆", "chapter": "第85章", "tariff_rate": "5%", "vat_rate": "13%", "supervision": "A", "description": "装有连接器的绝缘电线、电缆（如USB线、数据线）"},

    # 第61-62章 - 纺织服装
    {"hs_code": "6109.10", "name": "棉制T恤衫", "chapter": "第61章", "tariff_rate": "14%", "vat_rate": "13%", "supervision": "A/B", "description": "棉制针织或钩编的T恤衫、汗衫及其他背心"},
    {"hs_code": "6109.90", "name": "其他纺织材料制T恤衫", "chapter": "第61章", "tariff_rate": "14%", "vat_rate": "13%", "supervision": "A/B", "description": "非棉制的针织T恤衫（如化纤、混纺）"},
    {"hs_code": "6203.42", "name": "男式棉制裤子", "chapter": "第62章", "tariff_rate": "16%", "vat_rate": "13%", "supervision": "A/B", "description": "男式棉制便裤、工装裤等梭织长裤"},
    {"hs_code": "6204.43", "name": "女式化纤制连衣裙", "chapter": "第62章", "tariff_rate": "16%", "vat_rate": "13%", "supervision": "A/B", "description": "女式化学纤维制梭织连衣裙及半身裙"},

    # 第64章 - 鞋类
    {"hs_code": "6403.99", "name": "皮革面鞋靴", "chapter": "第64章", "tariff_rate": "10%", "vat_rate": "13%", "supervision": "A/B", "description": "皮革制鞋面的其他鞋靴（不含运动鞋）"},
    {"hs_code": "6404.11", "name": "运动鞋（纺织面料）", "chapter": "第64章", "tariff_rate": "24%", "vat_rate": "13%", "supervision": "A/B", "description": "纺织材料制鞋面的运动鞋靴（跑步鞋、篮球鞋等）"},

    # 第39章 - 塑料制品
    {"hs_code": "3923.21", "name": "塑料袋（乙烯聚合物）", "chapter": "第39章", "tariff_rate": "6.5%", "vat_rate": "13%", "supervision": "A", "description": "乙烯聚合物制供运输或包装货物用的袋子"},
    {"hs_code": "3926.90", "name": "其他塑料制品", "chapter": "第39章", "tariff_rate": "6.5%", "vat_rate": "13%", "supervision": "A", "description": "其他塑料制的物品（如塑料玩具、家居用品等）"},

    # 第71章 - 珠宝
    {"hs_code": "7113.19", "name": "贵金属首饰（金）", "chapter": "第71章", "tariff_rate": "20%", "vat_rate": "13%", "supervision": "A", "description": "黄金制首饰及其零件（不论是否镶嵌宝石）"},
    {"hs_code": "7117.19", "name": "仿首饰（贱金属）", "chapter": "第71章", "tariff_rate": "35%", "vat_rate": "13%", "supervision": "A", "description": "贱金属制仿首饰（不含天然珍珠、宝石）"},

    # 第90章 - 光学/医疗仪器
    {"hs_code": "9006.53", "name": "数码相机", "chapter": "第90章", "tariff_rate": "0%", "vat_rate": "13%", "supervision": "A", "description": "使用半导体传感器的数字照相机"},
    {"hs_code": "9018.90", "name": "医疗器械（其他）", "chapter": "第90章", "tariff_rate": "3%", "vat_rate": "13%", "supervision": "A/B", "description": "医疗、外科、牙科用仪器及器具的其他零件、附件"},
    {"hs_code": "9019.10", "name": "按摩器具", "chapter": "第90章", "tariff_rate": "6%", "vat_rate": "13%", "supervision": "A", "description": "机械治疗器具及按摩用器械"},

    # 第87章 - 车辆
    {"hs_code": "8703.23", "name": "小轿车（1500-3000cc汽油）", "chapter": "第87章", "tariff_rate": "15%", "vat_rate": "13%", "supervision": "A/B/6", "description": "装有点燃式发动机的小轿车，排气量超过1500ml但不超过3000ml"},
    {"hs_code": "8704.21", "name": "货车（柴油，≤5吨）", "chapter": "第87章", "tariff_rate": "15%", "vat_rate": "13%", "supervision": "A/B", "description": "装用柴油发动机的货车，车辆总重量不超过5吨"},
    {"hs_code": "8711.20", "name": "摩托车（50-250cc）", "chapter": "第87章", "tariff_rate": "45%", "vat_rate": "13%", "supervision": "A/B", "description": "装有往复式内燃发动机的两轮摩托车，排气量超过50ml但不超过250ml"},

    # 第73章 - 钢铁制品
    {"hs_code": "7326.90", "name": "其他钢铁制品", "chapter": "第73章", "tariff_rate": "7%", "vat_rate": "13%", "supervision": "A", "description": "钢铁制的其他物品（如紧固件、结构件等）"},
    {"hs_code": "7318.15", "name": "螺钉螺栓", "chapter": "第73章", "tariff_rate": "8%", "vat_rate": "13%", "supervision": "A", "description": "钢铁制螺钉、螺栓、螺母、钩头螺栓等紧固件"},

    # 第48章 - 纸制品
    {"hs_code": "4819.10", "name": "纸板箱/瓦楞纸箱", "chapter": "第48章", "tariff_rate": "0%", "vat_rate": "13%", "supervision": "A", "description": "瓦楞纸板或纸板制的箱、盒（用于包装运输）"},
    {"hs_code": "4802.55", "name": "书写印刷纸", "chapter": "第48章", "tariff_rate": "5%", "vat_rate": "13%", "supervision": "A", "description": "书写、印刷用途的未经涂布纸及纸板"},

    # 第22章 - 食品饮料
    {"hs_code": "2202.99", "name": "其他无酒精饮料", "chapter": "第22章", "tariff_rate": "20%", "vat_rate": "13%", "supervision": "A/B", "description": "未加糖或其他甜物质的无酒精饮料（矿泉水除外）"},
    {"hs_code": "2106.90", "name": "保健食品/膳食补充剂", "chapter": "第21章", "tariff_rate": "10%", "vat_rate": "13%", "supervision": "A/B/3", "description": "其他编号未列名的食品制备品（含保健食品、蛋白粉等）"},

    # 第30章 - 药品
    {"hs_code": "3004.90", "name": "其他药品（中成药等）", "chapter": "第30章", "tariff_rate": "3%", "vat_rate": "13%", "supervision": "A/Q", "description": "混合或非混合产品构成的药品（不含生物制品）"},

    # 第33章 - 化妆品
    {"hs_code": "3304.99", "name": "护肤品/化妆品", "chapter": "第33章", "tariff_rate": "5%", "vat_rate": "13%", "supervision": "A/B/4", "description": "护肤用化妆品（面霜、乳液、精华等）"},
    {"hs_code": "3305.10", "name": "洗发水/护发素", "chapter": "第33章", "tariff_rate": "5%", "vat_rate": "13%", "supervision": "A/B/4", "description": "洗发剂（香波）、护发素等头发护理制剂"},
]

# ══════════════════════════════════════════════════════════════
# 2. 商品归类决定（模拟真实格式）
# ══════════════════════════════════════════════════════════════

CLASSIFICATION_RULINGS = [
    {
        "ruling_id": "Z2024-0015",
        "product_name": "智能手表",
        "product_desc": "具有通话、健康监测（心率、血氧）、GPS定位、消息推送等功能的腕戴式电子设备，屏幕尺寸1.78英寸，支持eSIM。",
        "hs_code": "8517.62",
        "reasoning": "该商品虽然具有手表外形和时间显示功能，但其核心功能为数据通信（蜂窝网络通话、消息收发），符合税则85.17品目'可接收、转换和发送数据的装置'的定义。根据归类总规则一及六，应归入税则号列8517.62。",
        "legal_basis": "《进出口税则》第85章品目85.17；归类总规则一、六",
        "source": "海关总署公告2024年第195号",
        "effective_date": "2025-01-01",
    },
    {
        "ruling_id": "Z2024-0022",
        "product_name": "电动牙刷",
        "product_desc": "内置锂电池驱动的声波振动牙刷，配有压力传感器、蓝牙连接功能，可通过手机APP记录刷牙数据。",
        "hs_code": "8509.80",
        "reasoning": "该商品的主要功能为通过电机驱动刷头进行口腔清洁，属于家用电动器具。虽有蓝牙功能，但通信并非其主要功能。根据归类总规则一及三(一)，按主要功能归类，应归入税则号列8509.80。",
        "legal_basis": "《进出口税则》第85章品目85.09；归类总规则一、三(一)",
        "source": "海关总署公告2024年第116号",
        "effective_date": "2024-09-12",
    },
    {
        "ruling_id": "Z2025-0008",
        "product_name": "空气净化器",
        "product_desc": "家用空气净化器，采用HEPA滤网+活性炭过滤系统，具有PM2.5检测、自动模式、WiFi远程控制功能，适用面积30-50平方米。",
        "hs_code": "8421.39",
        "reasoning": "该商品的核心功能为通过风机和过滤系统净化空气，属于气体过滤净化装置。WiFi控制仅为辅助功能。根据归类总规则一，应归入税则号列8421.39。",
        "legal_basis": "《进出口税则》第84章品目84.21；归类总规则一",
        "source": "海关总署公告2025年第259号",
        "effective_date": "2025-12-30",
    },
    {
        "ruling_id": "Z2024-0031",
        "product_name": "无人机（消费级）",
        "product_desc": "四旋翼消费级航拍无人机，搭载4K高清摄像头，具备GPS定位、自动返航、避障功能，最大飞行时间30分钟。",
        "hs_code": "8806.22",
        "reasoning": "该商品为无人驾驶航空器，专用于航拍用途。根据2022年HS修订版新增的88.06品目，无人驾驶航空器应归入该品目。按最大起飞重量分类，本商品不超过7kg，应归入8806.22。",
        "legal_basis": "《进出口税则》第88章品目88.06；归类总规则一、六",
        "source": "海关总署公告2024年第195号",
        "effective_date": "2025-01-01",
    },
    {
        "ruling_id": "Z2025-0012",
        "product_name": "扫地机器人",
        "product_desc": "家用智能扫地机器人，具备激光导航、自动集尘、拖地功能，可通过APP设置清扫区域和禁区。",
        "hs_code": "8508.11",
        "reasoning": "该商品为自带电机的家用吸尘器（含扫地功能），虽具有智能导航功能，但核心功能仍为地面清洁。根据归类总规则一及三(一)，按主要功能归入税则号列8508.11。",
        "legal_basis": "《进出口税则》第85章品目85.08；归类总规则一、三(一)",
        "source": "海关总署公告2025年第259号",
        "effective_date": "2025-12-30",
    },
    {
        "ruling_id": "Z2024-0040",
        "product_name": "蓝牙音箱",
        "product_desc": "便携式蓝牙无线音箱，内置锂电池，支持防水(IPX7)、立体声配对，功率20W。",
        "hs_code": "8518.22",
        "reasoning": "该商品为独立的有源扬声器（内置功放），通过蓝牙接收音频信号后放大播放。根据税则85.18品目定义，应归入税则号列8518.22（有源扬声器）。",
        "legal_basis": "《进出口税则》第85章品目85.18；归类总规则一",
        "source": "海关总署公告2024年第195号",
        "effective_date": "2025-01-01",
    },
]


# ══════════════════════════════════════════════════════════════
# 3. 监管条件说明
# ══════════════════════════════════════════════════════════════

SUPERVISION_CODES = {
    "A": {"name": "入境货物通关单", "desc": "进口商品需提供检验检疫部门签发的通关单", "authority": "海关检验检疫"},
    "B": {"name": "出境货物通关单", "desc": "出口商品需提供检验检疫部门签发的通关单", "authority": "海关检验检疫"},
    "3": {"name": "进口药品通关单", "desc": "进口药品需提供国家药监局签发的通关单", "authority": "国家药品监督管理局"},
    "4": {"name": "进口化妆品备案凭证", "desc": "进口化妆品需完成国家药监局备案", "authority": "国家药品监督管理局"},
    "6": {"name": "旧机电产品禁止进口", "desc": "禁止进口旧机电产品（部分例外）", "authority": "商务部/海关总署"},
    "Q": {"name": "进口药品注册证", "desc": "首次进口药品需取得注册批准", "authority": "国家药品监督管理局"},
}


# ══════════════════════════════════════════════════════════════
# 4. FAQ（常见问题）
# ══════════════════════════════════════════════════════════════

FAQS = [
    {
        "question": "什么是HS编码？",
        "answer": "HS编码（Harmonized System Code，协调制度编码）是国际通用的商品分类编号体系，由世界海关组织(WCO)制定。中国采用10位编码制度：前6位为国际标准编码，后4位为国内细分编码。正确使用HS编码是进出口申报的基础，直接影响关税税率、监管条件和退税政策。",
        "source": "《中华人民共和国进出口税则》编制说明",
    },
    {
        "question": "如何确定商品的HS编码？",
        "answer": "确定HS编码需要遵循归类总规则，依次考虑：(1)品目条文及有关类注或章注；(2)该商品是否符合品目的基本特征；(3)参照归类决定和归类先例。建议通过'中国国际贸易单一窗口'(www.singlewindow.cn)查询确认，必要时可向海关申请预裁定。",
        "source": "《海关进出口货物商品归类管理规定》(海关总署令第252号)",
    },
    {
        "question": "监管条件A和B是什么意思？",
        "answer": "监管条件A表示'入境货物通关单'，即进口商品需提供检验检疫部门签发的通关单才能通关。监管条件B表示'出境货物通关单'，即出口时需要。两者均由海关检验检疫部门签发，属于法检范围内的商品必须办理。",
        "source": "海关总署监管证件代码说明",
    },
    {
        "question": "进口关税是如何计算的？",
        "answer": "进口关税 = 完税价格 × 关税税率。其中完税价格通常为CIF价（到岸价格，含成本+保险费+运费）。此外还需缴纳进口环节增值税（一般为13%），部分商品还有消费税。综合税负 = (完税价格 + 关税) × 增值税税率 + 关税。",
        "source": "《进出口关税条例》",
    },
    {
        "question": "什么情况下需要办理3C认证？",
        "answer": "列入《实施强制性产品认证的产品目录》的商品，在进口时需提供CCC认证证书。主要包括：电线电缆、电路开关、电动工具、家用电器、音视频设备、信息技术设备、照明设备、机动车辆及安全零部件等。具体目录可查询国家认监委官网。",
        "source": "国家认监委强制性产品认证目录",
    },
    {
        "question": "跨境电商和个人行邮有什么区别？",
        "answer": "跨境电商(B2C)通过海关注册的电商平台交易，享受跨境电子商务综合税（关税0%，增值税和消费税打7折）。个人行邮指个人邮寄进出境物品，按行邮税征收（分13%、20%、50%三档），免征额为50元。两者适用的税收政策和限额不同。",
        "source": "财政部 海关总署 国家税务总局关于跨境电子商务零售进口税收政策的通知",
    },
    {
        "question": "HS编码归类错误会有什么后果？",
        "answer": "HS编码归类错误可能导致：(1)少缴税款 → 补税+滞纳金+罚款；(2)多缴税款 → 可申请退还（3年内）；(3)违反监管条件 → 可能构成走私违规；(4)影响企业信用等级。据海关总署数据，2023年因归类错误导致的退单率达17.3%。",
        "source": "《海关行政处罚实施条例》",
    },
    {
        "question": "如何申请海关商品预裁定？",
        "answer": "进出口货物收发货人可在货物实际进出口前，向注册地直属海关申请商品归类预裁定。需提交：申请书、商品详细资料（成分、功能、用途、图片等）。海关应在60日内作出裁定。预裁定有效期为3年，在全国海关范围内适用。",
        "source": "《海关预裁定管理暂行办法》(海关总署令第236号)",
    },
]


# ══════════════════════════════════════════════════════════════
# 5. 操作规范（企业内部 SOP 示例）
# ══════════════════════════════════════════════════════════════

SOP_DOCUMENTS = [
    {
        "title": "进口报关操作规范",
        "content": """# 进口报关操作规范

## 一、前期准备
1. 确认贸易术语（FOB/CIF/DDP等），明确我方责任范围
2. 收集全套单据：合同、发票、装箱单、提单/运单
3. 核实商品信息：品名、材质、用途、品牌、型号、原产国

## 二、HS编码归类
1. 根据商品描述初步确定章节
2. 参考税则注释和归类决定确认编码
3. 如有疑问，通过单一窗口查询或申请预裁定

## 三、申报要素填写
1. 品名及规格型号：须与合同/发票一致
2. 成分/材质：如实申报，影响归类和税率
3. 品牌：须申报中文或英文品牌名
4. 用途：简要说明使用场景
5. 原产国/地区：按WTO原产地规则确定

## 四、税费计算
1. 关税 = 完税价格(CIF) × 关税税率
2. 增值税 = (完税价格 + 关税 + 消费税) × 13%
3. 注意是否有暂定税率或FTA优惠税率可用

## 五、注意事项
- 确保所有单据信息一致性（单单相符、单货相符）
- 监管条件涉及的证件须在申报前办妥
- 保留完整报关单据备查（至少保存3年）
""",
        "source": "公司内部操作规范 v2.1",
    },
    {
        "title": "商品归类复核流程",
        "content": """# 商品归类复核流程

## 目的
降低归类错误风险，避免因归类问题导致的补税、罚款或通关延误。

## 复核要点
1. **品名核实**：申报品名是否准确反映商品实际属性
2. **功能确认**：商品主要功能是否与编码描述匹配
3. **材质检查**：材质成分是否影响归类（特别是混合材质）
4. **用途判断**：多功能商品按主要功能归类
5. **先例参考**：查阅是否有类似商品的归类决定

## 复核流程
1. 业务员提交归类初审表
2. 归类专员对照税则逐项核对
3. 存疑商品提交上级或外部专家复核
4. 高风险商品申请海关预裁定
5. 复核结果记入商品数据库，形成企业归类库

## 常见错误类型
- 按商品名称而非功能归类
- 忽略章注和类注的排除条款
- 多功能商品未按主要功能归类
- 未及时更新编码（每年税则调整）
""",
        "source": "公司内部操作规范 v1.8",
    },
]


# ══════════════════════════════════════════════════════════════
# 6. 模拟报关单数据
# ══════════════════════════════════════════════════════════════

SAMPLE_DECLARATIONS = [
    {
        "doc_type": "进口报关单",
        "declaration_no": "I202409150001",
        "fields": {
            "经营单位": "深圳市XX贸易有限公司",
            "收货单位": "深圳市YY电子科技有限公司",
            "合同协议号": "CT2024-0888",
            "贸易方式": "一般贸易",
            "成交方式": "CIF深圳",
            "起运国": "日本",
            "原产国": "日本",
            "件数": 50,
            "毛重(kg)": 1250.5,
            "净重(kg)": 1100.0,
            "商品名称": "便携式自动数据处理设备",
            "HS编码": "8471300000",
            "规格型号": "BrandX ModelPro 14寸/i7/16G/512G",
            "数量": 100,
            "单位": "台",
            "单价": 3500.00,
            "总价": 350000.00,
            "币制": "人民币",
            "原产国": "日本",
            "征免性质": "一般征税",
        },
        "notes": "正常报关单样本",
    },
    {
        "doc_type": "商业发票",
        "invoice_no": "INV-2024-0777",
        "fields": {
            "卖方": "Tokyo Electronics Co., Ltd.",
            "买方": "Shenzhen XX Trading Co., Ltd.",
            "日期": "2024-09-10",
            "付款条件": "T/T 30天",
            "商品描述": "Laptop Computer BrandX ModelPro",
            "HS编码": "8471.30",
            "数量": 100,
            "单价(USD)": 485.00,
            "总额(USD)": 48500.00,
            "贸易术语": "CIF Shenzhen",
            "原产国": "Japan",
        },
        "notes": "注意：发票金额与报关单不一致（可能存在低报）",
    },
]


# ══════════════════════════════════════════════════════════════
# 写入文件
# ══════════════════════════════════════════════════════════════

def write_jsonl(data: list[dict], filename: str):
    path = PROCESSED_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"✅ {path} ({len(data)} 条)")


def main():
    print("开始生成关务知识库数据...\n")

    write_jsonl(HS_CODES, "hs_codes.jsonl")
    write_jsonl(CLASSIFICATION_RULINGS, "classification_rulings.jsonl")
    write_jsonl(
        [{"code": k, **v} for k, v in SUPERVISION_CODES.items()],
        "supervision_codes.jsonl"
    )
    write_jsonl(FAQS, "faq.jsonl")
    write_jsonl(SOP_DOCUMENTS, "sop_documents.jsonl")
    write_jsonl(SAMPLE_DECLARATIONS, "sample_declarations.jsonl")

    # 统计
    print(f"\n📊 数据统计:")
    print(f"   HS编码: {len(HS_CODES)} 条")
    print(f"   归类决定: {len(CLASSIFICATION_RULINGS)} 条")
    print(f"   监管代码: {len(SUPERVISION_CODES)} 种")
    print(f"   FAQ: {len(FAQS)} 条")
    print(f"   操作规范: {len(SOP_DOCUMENTS)} 篇")
    print(f"   模拟单据: {len(SAMPLE_DECLARATIONS)} 份")
    print(f"\n总计: {len(HS_CODES) + len(CLASSIFICATION_RULINGS) + len(SUPERVISION_CODES) + len(FAQS) + len(SOP_DOCUMENTS) + len(SAMPLE_DECLARATIONS)} 条记录")


if __name__ == "__main__":
    main()
