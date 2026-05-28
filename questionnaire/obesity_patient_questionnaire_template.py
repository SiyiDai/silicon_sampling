from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


ORIGINAL_DOCX = (
    "questionnaire/Obesity and MASH Patient Buying Process Study_Obesity Patient "
    "Quantitative QNR 05-08-26.docx"
)


@dataclass(frozen=True)
class Option:
    code: str
    label: str
    group: str = ""
    note: str = ""


@dataclass(frozen=True)
class QuestionSpec:
    qid: str
    section: str
    stem: str
    response_type: str
    answer_format: str
    options: tuple[Option, ...] = ()
    rows: tuple[Option, ...] = ()
    columns: tuple[Option, ...] = ()
    show_if: str = ""
    validations: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()


def opt(code: object, label: str, group: str = "", note: str = "") -> Option:
    return Option(code=str(code), label=label, group=group, note=note)


def q(
    qid: str,
    section: str,
    stem: str,
    response_type: str,
    answer_format: str,
    *,
    options: Sequence[Option] = (),
    rows: Sequence[Option] = (),
    columns: Sequence[Option] = (),
    show_if: str = "",
    validations: Sequence[str] = (),
    notes: Sequence[str] = (),
) -> QuestionSpec:
    return QuestionSpec(
        qid=qid,
        section=section,
        stem=stem,
        response_type=response_type,
        answer_format=answer_format,
        options=tuple(options),
        rows=tuple(rows),
        columns=tuple(columns),
        show_if=show_if,
        validations=tuple(validations),
        notes=tuple(notes),
    )


YES_NO = (opt(1, "是"), opt(2, "否"))

LIKERT_1_7 = tuple(opt(i, str(i)) for i in range(1, 8))
WILLINGNESS_0_10 = tuple(opt(i, str(i)) for i in range(0, 11))

CITY_TIER_OPTIONS = (
    opt(1, "一线城市"),
    opt(2, "二线城市"),
    opt(3, "三线城市"),
)

GENDER_OPTIONS = (opt(1, "男性"), opt(2, "女性"))

AGE_SEGMENT_OPTIONS = (
    opt(1, "青年：18-30岁"),
    opt(2, "中年：男性31-60岁；女性31-55岁"),
    opt(3, "老年：男性60岁以上；女性55岁以上"),
)

BMI_CATEGORY_OPTIONS = (
    opt(1, "BMI>28"),
    opt(2, "24<BMI<=28"),
    opt(3, "BMI<=24"),
)

COMORBIDITY_OPTIONS = (
    opt(1, "代谢相关脂肪性肝病（脂肪肝、脂肪性肝炎、脂肪性肝纤维化、脂肪性肝硬化）", "合并症/基础病"),
    opt(2, "糖尿病", "合并症/基础病"),
    opt(3, "高血压", "合并症/基础病"),
    opt(4, "高脂血症", "合并症/基础病"),
    opt(5, "高尿酸血症", "合并症/基础病"),
    opt(6, "阻塞性睡眠呼吸暂停", "合并症/基础病"),
    opt(7, "多囊卵巢综合征", "合并症/基础病"),
    opt(8, "心梗（包括既往经历过）", "合并症/基础病"),
    opt(9, "脑梗", "合并症/基础病"),
    opt(10, "冠心病", "合并症/基础病"),
    opt(11, "膝关节受损（如疼痛、僵硬等）", "合并症/基础病"),
    opt(12, "血糖偏高，但未确诊糖尿病", "指标异常"),
    opt(13, "血压偏高，但未确诊高血压", "指标异常"),
    opt(14, "血脂偏高，但未确诊高脂血症", "指标异常"),
    opt(15, "尿酸偏高，但未确诊高尿酸血症", "指标异常"),
    opt(16, "肝脏脂肪浸润，但未确诊代谢相关脂肪性肝病", "指标异常"),
    opt(97, "其他，请注明"),
    opt(99, "以上合并症/基础病和指标异常均没有", note="与其他选项互斥"),
)

MASH_SUBTYPE_OPTIONS = (
    opt(1, "单纯性脂肪肝（代谢脂肪肝病早期）"),
    opt(2, "早期代谢相关脂肪性肝炎（MASH F0-1）"),
    opt(3, "代谢相关脂肪性肝纤维化（MASH F2）"),
    opt(4, "代谢相关脂肪性肝纤维化（MASH F3）"),
    opt(5, "代谢相关脂肪性肝硬化（MASH F4）"),
    opt(98, "不清楚具体分型"),
)

WEIGHT_METHOD_OPTIONS = (
    opt(1, "食用代餐（奶昔、能量棒、代餐粉等）", "控制饮食"),
    opt(2, "调整饮食习惯为低盐/低油/低碳水", "控制饮食"),
    opt(3, "服用减肥茶", "减肥产品"),
    opt(4, "服用保健品（左旋肉碱、消化酶、排毒养颜胶囊、通便凝胶等）", "减肥产品"),
    opt(5, "服用中药", "中医"),
    opt(6, "针灸", "中医"),
    opt(7, "经络推拿、按摩", "中医"),
    opt(8, "埋线", "中医"),
    opt(9, "跑步、慢走", "运动"),
    opt(10, "游泳、羽毛球等专项运动", "运动"),
    opt(11, "健身、瑜伽、普拉提等私教课程", "运动"),
    opt(12, "奥利司他", "减重西药"),
    opt(13, "GLP-1药物（司美格鲁肽、替尔泊肽、利拉鲁肽、玛仕度肽等）", "减重西药"),
    opt(14, "减重手术（袖状胃切除术、胃旁路术、胆胰转流十二指肠转位术、抽脂手术等）", "减重手术"),
    opt(99, "以上措施均未尝试过", note="与其他选项互斥"),
)

NON_MEDICAL_WEIGHT_METHOD_ROWS = WEIGHT_METHOD_OPTIONS[:11]

NON_MEDICAL_WEIGHT_METHOD_GROUPS = (
    opt(1, "饮食调整"),
    opt(2, "减肥产品"),
    opt(3, "中医"),
    opt(4, "运动"),
)

DEPARTMENT_OPTIONS = (
    opt(1, "内分泌科"),
    opt(2, "减重门诊"),
    opt(3, "减重手术外科"),
    opt(4, "营养科"),
    opt(5, "心内科"),
    opt(6, "肝内科"),
    opt(7, "消化内科"),
    opt(8, "中医科"),
    opt(9, "妇科"),
    opt(97, "其他科室，请注明"),
)

PRESCRIBED_TREATMENT_OPTIONS = (
    opt(1, "奥利司他"),
    opt(2, "GLP-1药物（司美格鲁肽、替尔泊肽、利拉鲁肽、玛仕度肽等）"),
    opt(3, "降糖药物（二甲双胍、吡格列酮、列净类药物等）"),
    opt(4, "减重手术"),
)

GLP1_BRAND_OPTIONS = (
    opt(1, "利拉鲁肽（诺和力、利鲁平）"),
    opt(2, "贝那鲁肽（菲塑美、谊生泰）"),
    opt(3, "司美格鲁肽（诺和盈、诺和泰）"),
    opt(4, "替尔泊肽（穆峰达）"),
    opt(5, "玛仕度肽（信尔美）"),
    opt(6, "埃诺格鲁肽（先维盈、先颐达）"),
)

CORE_GLP1_BRAND_COLUMNS = (
    opt("A", "司美格鲁肽（诺和盈、诺和泰）"),
    opt("B", "替尔泊肽（穆峰达）"),
    opt("C", "玛仕度肽（信尔美）"),
    opt("D", "埃诺格鲁肽（先维盈、先颐达）"),
)

GLP1_DECISION_FACTOR_OPTIONS = (
    opt(1, "线下医院医生推荐"),
    opt(2, "互联网医院/线上问诊医生推荐"),
    opt(3, "药房药师推荐"),
    opt(4, "身边亲友经验分享与推荐"),
    opt(5, "社交媒体用户经验分享与推荐"),
    opt(6, "网红、明星、企业家等知名人士的经验分享与推荐"),
    opt(7, "受到该品牌推广广告吸引"),
    opt(97, "其他，请注明"),
)

INFO_CHANNEL_OPTIONS = (
    opt(1, "线下实体医院", "线下"),
    opt(2, "和亲朋好友/同事聊天", "线下"),
    opt(3, "线下零售药店药剂师/店员", "线下"),
    opt(4, "线上问诊平台（好大夫、平安好医生、微医、丁香医生等）", "线上"),
    opt(5, "微信群聊", "线上"),
    opt(6, "微信公众号", "线上"),
    opt(7, "抖音", "线上"),
    opt(8, "小红书", "线上"),
    opt(9, "微博", "线上"),
    opt(10, "知乎", "线上"),
    opt(11, "快手", "线上"),
    opt(12, "今日头条", "线上"),
    opt(13, "Bilibili 哔哩哔哩"),
    opt(14, "豆瓣"),
    opt(15, "百度"),
    opt(16, "AI（蚂蚁阿福、豆包、Deepseek等）"),
    opt(97, "其他，请注明"),
)

GLP1_EVALUATION_ROWS = (
    opt(0, "总体满意度"),
    opt(1, "起效速度快", "减重疗效"),
    opt(2, "减重效果好", "减重疗效"),
    opt(3, "减重效果持续，没有减重平台期", "减重疗效"),
    opt(4, "停药后不反弹", "减重疗效"),
    opt(5, "腰围下降明显", "减重疗效"),
    opt(6, "代谢合并症得到改善（血糖、血脂、血压、尿酸等）", "减重质量"),
    opt(7, "内脏脂肪减少", "减重质量"),
    opt(8, "肌肉量流失较少", "减重质量"),
    opt(9, "生活质量和日常生活能力提升", "减重质量"),
    opt(10, "衣服穿起来更合身", "减重质量"),
    opt(11, "副作用发生率低（恶心、呕吐、腹泻等）", "安全性"),
    opt(12, "副作用严重程度低，不影响日常生活和工作", "安全性"),
    opt(13, "用药便利、创伤小", "便利性"),
    opt(14, "调整剂量的挡位数量合适", "便利性"),
    opt(15, "给药频率（如日制剂、周制剂）", "便利性"),
    opt(16, "经过专业医生推荐", "口碑/可靠性"),
    opt(17, "经过身边亲友推荐", "口碑/可靠性"),
    opt(18, "购药方便（电商、药店等渠道）", "可及性"),
    opt(19, "价格可接受", "经济性"),
    opt(20, "医保可报销", "经济性"),
)

PURCHASE_CHANNEL_OPTIONS = (
    opt(1, "医院"),
    opt(2, "电商"),
    opt(3, "药房"),
    opt(4, "医美机构"),
    opt(97, "其他，请注明"),
)

ECOMMERCE_PLATFORM_OPTIONS = (
    opt(1, "阿里健康大药房"),
    opt(2, "淘宝/天猫上的药物专营店、大药房旗舰店"),
    opt(3, "淘宝闪购/饿了么上的药物专营店、大药房旗舰店"),
    opt(4, "京东大药房"),
    opt(5, "京东健康互联网医院"),
    opt(6, "京东上的药物专营店、大药房旗舰店"),
    opt(7, "美团自营大药房"),
    opt(8, "美团买药上的药物专营店、大药房旗舰店"),
    opt(9, "叮当快药"),
    opt(10, "拼多多上的药物专营店、大药房旗舰店"),
    opt(97, "其他，请注明"),
)

PRODUCT_COLUMNS = (
    opt("X", "产品X"),
    opt("A", "产品A"),
    opt("B", "产品B"),
    opt("C", "产品C"),
)

PRODUCT_CARD = {
    "产品X": {
        "作用机制": "GLP-1R/GCGR 双靶点激动剂",
        "治疗疾病布局": "长期体重管理；MASH（纤维化F2-F4）；不含2型糖尿病适应症",
        "使用方式": "皮下注射，每周一次；0.3/0.6/1.2/2.4/3.6/4.8mg 阶梯式剂量爬坡",
        "减重疗效": "全球数据：76周体重降幅13.4%；中国数据暂无",
        "代谢获益": "腰围下降16.6cm（46周）；糖化血红蛋白下降1.68%（16周）；收缩压下降9.2mmHg（46周）；舒张压下降4.7mmHg（46周）",
        "安全性": "任何不良反应发生率91%；常见不良反应：恶心56%、呕吐27%、腹泻22%",
    },
    "产品A": {
        "作用机制": "GLP-1R/GIP 双靶点激动剂",
        "治疗疾病布局": "长期体重管理；MASH（纤维化F2-F3）；2型糖尿病",
        "使用方式": "皮下注射，每周一次；2.5/5/7.5/10/12.5/15mg 阶梯式剂量爬坡",
        "减重疗效": "全球数据：72周体重降幅17.8%；中国数据：52周体重降幅15.1%",
        "代谢获益": "腰围下降14.5cm（52周）；糖化血红蛋白下降2.07%（72周）；收缩压下降9mmHg（52周）；舒张压下降5.5mmHg（52周）",
        "安全性": "任何不良反应发生率90%；常见不良反应：恶心56%、呕吐27%、腹泻22%",
    },
    "产品B": {
        "作用机制": "GLP-1R 激动剂",
        "治疗疾病布局": "长期体重管理；MASH（纤维化F2-F3）；2型糖尿病",
        "使用方式": "皮下注射，每周一次；0.25/0.5/1/1.7/2.4mg 阶梯式剂量爬坡",
        "减重疗效": "全球数据：68周体重降幅12.4%；中国数据：44周体重降幅9.9%",
        "代谢获益": "腰围下降13.5cm（68周）；糖化血红蛋白下降1.6%（68周）；收缩压下降6.6mmHg（68周）；舒张压下降2.8mmHg（68周）",
        "安全性": "任何不良反应发生率90%；常见不良反应：恶心56%、呕吐27%、腹泻22%",
    },
    "产品C": {
        "作用机制": "GLP-1R/GCGR 双靶点激动剂",
        "治疗疾病布局": "长期体重管理；MASH（纤维化F2-F3）；2型糖尿病",
        "使用方式": "皮下注射，每周一次；2/4/6mg 阶梯式剂量爬坡",
        "减重疗效": "全球数据暂无；中国数据：48周体重降幅14.3%",
        "代谢获益": "腰围下降10.7cm（48周）；糖化血红蛋白下降1.73%（28周）；收缩压下降8.6mmHg（48周）；舒张压下降5.3mmHg（48周）",
        "安全性": "任何不良反应发生率97%；常见不良反应：恶心51%、呕吐43%、腹泻39%",
    },
}


QUESTIONNAIRE_ANALYSIS = (
    "该问卷包含甄别问卷和主问卷。甄别阶段用于筛掉行业相关人员、低教育程度、低收入、"
    "不满足BMI/合并症/减重经历条件的人群，并为城市线级、性别年龄、BMI、合并症和GLP-1使用经历建立配额。",
    "主问卷A部分聚焦减重旅程：理念、驱动因素、目标、非西医减重措施、到院路径、科室转换、合并症就诊、院内处方、随访。",
    "主问卷B部分聚焦GLP-1：知晓未用原因、未来意愿、选择因素、品牌使用、决策渠道、剂量滴定、停药换药、坚持用药支持、购药和续药渠道。",
    "主问卷C部分是新产品和商品名测试，产品示卡原文在Word中以图片呈现，已在PRODUCT_CARD中转写为可用于Prompt的文本。",
    "主问卷D部分收集基本情况和减重观念，包括工作、家庭、照护责任、健康理念、理想支持工具。",
)


QUESTIONNAIRE: tuple[QuestionSpec, ...] = (
    q(
        "CONSENT",
        "知情同意",
        "是否同意研究收集并按项目需要使用您的个人信息；涉及药品不良事件时，相关患者信息可能披露给客户公司药品不良反应监管部门并依法上报。",
        "single",
        "返回 1 或 2；若为2，后续题留空。",
        options=(opt(1, "同意"), opt(2, "不同意")),
    ),
    q(
        "S1",
        "甄别问卷",
        "您和同住的家人有没有在以下行业工作的？",
        "single",
        "返回一个代码。",
        options=(
            opt(1, "市场研究公司或其他公司的市场研究部门", note="终止甄别"),
            opt(2, "广告或公关公司或其他公司的广告/公关部门", note="终止甄别"),
            opt(3, "报社/杂志社/电台/电视台", note="终止甄别"),
            opt(4, "制药厂/制药公司/医疗卫生行业", note="终止甄别"),
            opt(5, "以上皆无", note="继续"),
        ),
    ),
    q(
        "S2",
        "甄别问卷",
        "请问您所在的城市线级是？",
        "single",
        "返回一个代码。",
        options=CITY_TIER_OPTIONS,
        notes=("一线城市目标30%，二线城市40%，三线城市30%。",),
    ),
    q(
        "S3",
        "甄别问卷",
        "请问您的性别是？",
        "single",
        "返回一个代码。",
        options=GENDER_OPTIONS,
    ),
    q(
        "S4",
        "甄别问卷",
        "请问您的年龄是多少周岁？并按规则归入年龄段。",
        "numeric_with_auto_category",
        "返回对象：{'age': 整数, 'segment': 年龄段代码}。",
        options=AGE_SEGMENT_OPTIONS,
        validations=("年龄段按性别自动匹配：男性31-60为中年，60岁以上为老年；女性31-55为中年，55岁以上为老年。",),
    ),
    q(
        "S5",
        "甄别问卷",
        "请问您的学历是？",
        "single",
        "返回一个代码。",
        options=(
            opt(1, "本科/大专及以上"),
            opt(2, "高中/中专"),
            opt(3, "初中及以下", note="终止甄别"),
        ),
    ),
    q(
        "S5A",
        "甄别问卷",
        "请问您家庭年收入为多少？请将所有家庭成员的收入都计算在内。",
        "single",
        "返回一个代码。",
        options=(
            opt(1, "10万人民币以上"),
            opt(2, "5-10万人民币"),
            opt(3, "1.7-5万人民币"),
            opt(4, "1.7万人民币以下", note="终止甄别"),
        ),
    ),
    q(
        "S6",
        "甄别问卷",
        "请问您的身高为多少厘米？当前体重为多少公斤？腰围为多少厘米？",
        "numeric_group",
        "返回对象：{'height_cm': 数字, 'weight_kg': 数字, 'waist_cm': 数字}。",
        validations=("身高限制120-199厘米。",),
    ),
    q(
        "S7",
        "甄别问卷",
        "根据S6自动计算当前BMI，并归入BMI分类。",
        "computed_single",
        "返回对象：{'bmi': 数字, 'category': 代码}。",
        options=BMI_CATEGORY_OPTIONS,
        validations=("BMI=体重kg / 身高m的平方。",),
    ),
    q(
        "S8",
        "甄别问卷",
        "请问您有以下哪些合并症/基础病或指标异常的情况？",
        "multi",
        "返回代码数组；97需给出文本；99与其他选项互斥。",
        options=COMORBIDITY_OPTIONS,
        validations=(
            "若S7=2且S8=97或99，终止甄别。",
            "2与12互斥，3与13互斥，4与14互斥，5与15互斥，1与16互斥。",
        ),
    ),
    q(
        "S9",
        "甄别问卷",
        "请问您目前代谢相关脂肪性肝病的分型是什么？",
        "single",
        "返回一个代码。",
        options=MASH_SUBTYPE_OPTIONS,
        show_if="仅S8=1时询问。",
    ),
    q(
        "S10",
        "甄别问卷",
        "请问您既往经历过以下哪些减重方式？",
        "multi",
        "返回代码数组；99与其他选项互斥。",
        options=WEIGHT_METHOD_OPTIONS,
        validations=(
            "若S7=3，必须选择13（GLP-1药物），否则终止甄别。",
            "若S7=1/2，必须覆盖至少3个减重措施大类，否则终止甄别。",
        ),
    ),
    q(
        "S11",
        "甄别问卷",
        "请问当您的身体出现异常时，您是否会积极就医，以维持健康的状态？",
        "single",
        "返回1或2。",
        options=YES_NO,
    ),
    q(
        "A1",
        "A 减重旅程",
        "请问您尝试减重总计多长时间了（从初次采取减重措施至今时长）？",
        "numeric_group",
        "返回对象：{'years': 整数, 'months': 整数, 'total_months': 整数}。",
        validations=("若不足1年，years填0；月份限制1-12；total_months为自动折算结果。",),
    ),
    q(
        "A2",
        "A 减重旅程",
        "以下哪个选项最能描述您对于体重问题的看法？",
        "single",
        "返回一个代码。",
        options=(
            opt(1, "超重/肥胖不是疾病，只是一种身体状态"),
            opt(2, "超重/肥胖通常不能算作疾病，但会引发各类健康问题"),
            opt(3, "超重/肥胖本身是一种需要医疗干预的慢性代谢疾病"),
        ),
    ),
    q(
        "A3",
        "A 减重旅程",
        "在您的减重经历中，您决心开始采取减重措施的驱动因素有哪些？",
        "multi",
        "返回代码数组；若选择97需给文本。",
        options=(
            opt(1, "体检结果显示存在异常代谢指标（血脂、血糖、肝酶等）"),
            opt(2, "因为体重问题引发身体不适（关节疼痛、睡眠呼吸暂停、月经不调等）"),
            opt(3, "在人生重要节点需要进行形象管理"),
            opt(4, "体重问题导致生活状态不佳（乏力、气短、低能量、行动不灵活等）"),
            opt(5, "体重问题影响工作或家庭投入"),
            opt(6, "萌生健康管理意识（提前预防代谢疾病等）"),
            opt(7, "体重问题影响心理健康（焦虑、沮丧、自卑、社交障碍等）"),
            opt(97, "其他，请注明"),
        ),
    ),
    q(
        "A3a",
        "A 减重旅程",
        "在A3勾选的驱动因素中，选出最重要的3项并排序。",
        "rank",
        "返回对象：{选项代码: 1/2/3}；只返回3项，不可重复。",
        show_if="仅对A3已选项排序。",
    ),
    q(
        "A4",
        "A 减重旅程",
        "请问您的减重目标有哪些？",
        "multi",
        "返回代码数组；若选择97需给文本。",
        options=(
            opt(1, "改善身体健康状况（已确诊合并症、已出现异常指标等）"),
            opt(2, "预防未来可能出现的疾病风险"),
            opt(3, "提升外在形象和自信"),
            opt(4, "让日常行动更轻便、减少身体重量负担"),
            opt(5, "能穿上喜欢的衣服或特定尺码"),
            opt(6, "改善精神状态，减少疲惫感和精力缺乏"),
            opt(7, "提升运动表现和体能"),
            opt(8, "更好地照顾家庭"),
            opt(97, "其他，请注明"),
        ),
    ),
    q(
        "A4a",
        "A 减重旅程",
        "在A4勾选的减重目标中，选出最重要的3项并排序。",
        "rank",
        "返回对象：{选项代码: 1/2/3}；只返回3项，不可重复。",
        show_if="仅对A4已选项排序。",
    ),
    q(
        "A5",
        "A 减重旅程",
        "请问您的目标体重是多少kg？",
        "numeric",
        "返回kg数字。",
        validations=("填写范围40kg至S6当前体重。",),
    ),
    q(
        "A5a",
        "A 减重旅程",
        "请问您希望达到目标体重的时长为多少个月？",
        "numeric",
        "返回整数月数。",
    ),
    q(
        "A6",
        "A 减重旅程",
        "针对经历过的非西医减重措施，分别填写尝试次数、单次平均坚持时长和月均花费。",
        "matrix_numeric",
        "返回对象：{方法代码: {'attempts': 整数, 'avg_months': 数字, 'monthly_cost_rmb': 整数}}。",
        rows=NON_MEDICAL_WEIGHT_METHOD_ROWS,
        show_if="仅S10包含1-11任一选项时询问；只出示S10已选的1-11项。",
        validations=("attempts需大于等于1；avg_months可一位小数；monthly_cost_rmb为整数。",),
    ),
    q(
        "A8",
        "A 减重旅程",
        "请您对这些非西医减重措施的减重效果满意度进行评价。",
        "matrix_rating_1_7",
        "返回对象：{措施大类代码: 1-7评分}。",
        rows=NON_MEDICAL_WEIGHT_METHOD_GROUPS,
        show_if="仅出示S10已选选项所属的大类。",
    ),
    q(
        "A9",
        "A 减重旅程",
        "请问您是否因为肥胖或肥胖相关合并症到医院就诊过？",
        "multi",
        "返回代码数组；3与其他选项互斥。",
        options=(
            opt(1, "曾到院就诊，以寻求减重方案"),
            opt(2, "曾到院就诊，以寻求肥胖相关合并症的治疗方案"),
            opt(3, "从未因为肥胖或肥胖相关合并症到院就诊过"),
        ),
        validations=("若S8=99，不出示选项2。",),
    ),
    q(
        "A10",
        "A 减重旅程",
        "请问您未曾前往医院寻求减重方案的原因有哪些？",
        "multi",
        "返回代码数组；97需给文本。",
        options=(
            opt(1, "肥胖不是疾病，无需就医"),
            opt(2, "目前暂未出现健康问题，无需就医"),
            opt(3, "目前体重不是很高，无需就医"),
            opt(4, "了解自己的身体并知道体重增长原因，决定自行减重"),
            opt(5, "不知道医院可以提供专业的体重管理方案"),
            opt(6, "不知道应该前往哪些科室"),
            opt(7, "不喜欢去医院"),
            opt(97, "其他，请注明"),
        ),
        show_if="仅A9不包含1时询问。",
    ),
    q(
        "A11",
        "A 减重旅程",
        "为了寻求减重治疗方案到院就诊时，最初前往和实际接受减重治疗是否在同一科室？",
        "single",
        "返回一个代码。",
        options=(
            opt(1, "是，在最初前往的科室接受了减重治疗"),
            opt(2, "否，最初科室就诊后，更换其他科室接受减重治疗"),
            opt(3, "仅到院咨询减重治疗方案，但未实际接受治疗"),
        ),
        show_if="仅A9包含1时询问。",
    ),
    q(
        "A12",
        "A 减重旅程",
        "请问您在哪个科室首诊并接受了减重治疗？",
        "single",
        "返回科室代码；97需给文本。",
        options=DEPARTMENT_OPTIONS,
        show_if="仅A11=1时询问。",
    ),
    q(
        "A13",
        "A 减重旅程",
        "您最初前往A12所选科室寻求减重治疗方案，最主要的原因是什么？",
        "single",
        "返回一个代码；97需给文本。",
        options=(
            opt(1, "询问导诊台，护士结合需求推荐了该科室"),
            opt(2, "在社交媒体、AI等互联网渠道了解到该科室可以提供减重治疗方案"),
            opt(3, "经朋友推荐前往该科室"),
            opt(4, "根据个人生活经验判断后前往"),
            opt(97, "其他原因，请注明"),
        ),
        show_if="仅A11=1时询问。",
    ),
    q(
        "A14_A15",
        "A 减重旅程",
        "最初前往哪个科室寻求减重治疗方案？最终实际在哪个科室接受减重治疗？",
        "dual_single",
        "返回对象：{'A14_first_department': 代码, 'A15_treatment_department': 代码}；97需给文本。",
        options=DEPARTMENT_OPTIONS,
        show_if="仅A11=2时询问。",
    ),
    q(
        "A16",
        "A 减重旅程",
        "您最初前往A14所选科室寻求减重治疗方案，最主要的原因是什么？",
        "single",
        "返回一个代码；97需给文本。",
        options=(
            opt(1, "询问导诊台，护士结合需求推荐了该科室"),
            opt(2, "在社交媒体、AI等互联网渠道了解到该科室可以提供减重治疗方案"),
            opt(3, "经朋友推荐前往该科室"),
            opt(4, "根据个人生活经验判断后前往"),
            opt(97, "其他原因，请注明"),
        ),
        show_if="仅A11=2时询问。",
    ),
    q(
        "A17",
        "A 减重旅程",
        "从A14首诊科室更换到A15治疗科室寻求减重治疗方案，最主要的原因是什么？",
        "single",
        "返回一个代码；97需给文本。",
        options=(
            opt(1, "首诊科室仅能提供减重建议，无法处方减重药物"),
            opt(2, "首诊科室无法进行减重手术"),
            opt(3, "首诊科室以减重手术为主要方案，想寻求药物减重方案"),
            opt(4, "想咨询不同科室医生的治疗建议"),
            opt(5, "首诊科室医生建议转到减重治疗更专业的科室"),
            opt(6, "对首诊科室医生的专业度或沟通方式不满意"),
            opt(97, "其他原因，请注明"),
        ),
        show_if="仅A11=2时询问。",
    ),
    q(
        "A18",
        "A 减重旅程",
        "曾因为哪些肥胖相关合并症/指标异常到院就诊？前往哪个科室？医生是否建议体重管理？",
        "matrix",
        "返回对象：{S8合并症代码: {'visited': 1/2, 'department': 科室代码或空, 'doctor_suggested_weight_management': 1/2或空}}。",
        rows=COMORBIDITY_OPTIONS[:-1],
        columns=DEPARTMENT_OPTIONS,
        show_if="仅A9包含2时询问；只出示S8已选合并症/指标异常。",
    ),
    q(
        "A19",
        "A 减重旅程",
        "您为肥胖相关合并症/指标异常就诊时，是否接受过减重药物治疗？",
        "single",
        "返回1或2。",
        options=YES_NO,
        show_if="仅A9包含2且A9不包含1时询问。",
    ),
    q(
        "A19a",
        "A 减重旅程",
        "您是在为哪个肥胖相关合并症/指标异常就诊时接受减重药物治疗的？",
        "single",
        "返回合并症代码；97需给文本。",
        options=COMORBIDITY_OPTIONS[:-1],
        show_if="仅A19=1时询问；只出示A18中医生建议体重管理的选项。",
    ),
    q(
        "A20",
        "A 减重旅程",
        "医生为您处方减重治疗方案中，包含以下哪些治疗方式？",
        "multi",
        "返回代码数组。",
        options=PRESCRIBED_TREATMENT_OPTIONS,
        show_if="仅A11=1/2或A19=1时询问。",
        validations=("需与S10中既往经历过的奥利司他、GLP-1、手术经历保持一致；若冲突，AI应优先保持全卷逻辑自洽。",),
    ),
    q(
        "A21",
        "A 减重旅程",
        "在和医生协商确定减重治疗方案时，GLP-1药物选择的决策权如何？",
        "single",
        "返回一个代码。",
        options=(
            opt(1, "医生建议使用GLP-1并推荐品牌，您接受该方案"),
            opt(2, "医生建议使用GLP-1，您提出倾向品牌，医生评估后为您处方"),
            opt(3, "医生建议使用GLP-1，您提出倾向品牌，医生建议更换品牌，您接受"),
            opt(4, "您希望使用GLP-1，医生推荐品牌，您接受"),
            opt(5, "您希望使用GLP-1，您提出倾向品牌，医生评估后为您处方"),
            opt(6, "您希望使用GLP-1，您提出倾向品牌，医生建议更换品牌，您接受"),
        ),
        show_if="仅A20包含2时询问。",
    ),
    q(
        "A22",
        "A 减重旅程",
        "接受减重手术治疗后体重下降多少kg？是否经历体重反弹，若反弹则反弹多少kg？",
        "numeric_group",
        "返回对象：{'loss_kg': 数字, 'rebounded': 1/2, 'rebound_kg': 数字或空}。",
        show_if="仅A20包含4时询问。",
    ),
    q(
        "A23",
        "A 减重旅程",
        "请问您在接受减重治疗后，是否定期到院复诊或随访？",
        "single",
        "返回1或2。",
        options=YES_NO,
    ),
    q(
        "A23a",
        "A 减重旅程",
        "请问您复诊或随访的频率如何？",
        "numeric",
        "返回对象：{'months_per_visit': 数字}。",
        show_if="仅A23=1时询问。",
    ),
    q(
        "B1",
        "B GLP-1药物选择与使用情况",
        "请问您是否知晓GLP-1药物可用于超重或肥胖症的减重治疗？",
        "single",
        "返回1或2。",
        options=YES_NO,
        show_if="仅S10不含13且A20不含2，即未使用过GLP-1用于减重时询问。",
    ),
    q(
        "B2",
        "B GLP-1药物选择与使用情况",
        "知晓GLP-1可用于减重但未曾尝试的原因是什么？",
        "multi",
        "返回代码数组；97需给文本。",
        options=(
            opt(1, "认为肥胖无需药物治疗，更倾向饮食、运动等方式减重"),
            opt(2, "担心效果不及预期"),
            opt(3, "担心副作用不耐受（恶心、呕吐、腹泻等）"),
            opt(4, "心理抵触注射类药物"),
            opt(5, "GLP-1药物价格较高，自费负担较大"),
            opt(6, "属于GLP-1禁忌症人群（胰腺炎、甲状腺疾病风险等）"),
            opt(7, "想尝试，但暂时还未落实行动"),
            opt(8, "担心长期持续使用造成药物依赖性"),
            opt(97, "其他原因，请注明"),
        ),
        show_if="仅B1=1时询问。",
    ),
    q(
        "B2a",
        "B GLP-1药物选择与使用情况",
        "您对未来尝试使用GLP-1药物用于减重的意愿如何？0分不会，10分一定会。",
        "rating_0_10",
        "返回0-10整数。",
        options=WILLINGNESS_0_10,
    ),
    q(
        "B3",
        "B GLP-1药物选择与使用情况",
        "选择GLP-1作为减重治疗药物时，以下考虑因素的重要程度分别如何？",
        "matrix_rating_1_7",
        "返回对象：{因素代码: 1-7评分}。",
        rows=GLP1_EVALUATION_ROWS[1:],
        validations=("纵向连续5个打分相同时应差异化；AI应避免机械全同分。",),
    ),
    q(
        "B4_B5",
        "B GLP-1药物选择与使用情况",
        "对您而言，GLP-1达到'起效速度快'和'减重效果好'的判断标准是什么？",
        "numeric_group",
        "返回对象：{'B4_fast_onset': {'weeks': 数字, 'weight_loss_pct': 数字}, 'B5_good_effect': {'months': 数字, 'weight_loss_pct': 数字}}。",
        show_if="B4仅B3-1>=5；B5仅B3-2>=5。",
    ),
    q(
        "B6",
        "B GLP-1药物选择与使用情况",
        "关于GLP-1药物调整剂量的挡位数量，哪一项与您的理念最相符？",
        "single",
        "返回1或2。",
        options=(
            opt(1, "爬坡剂量挡位越多越好，可自行选择爬坡速度，在疗效和不良反应间平衡"),
            opt(2, "爬坡剂量挡位越少越好，可快速达到维持剂量，避免频繁调整"),
        ),
        show_if="仅B3-14>=5时询问。",
    ),
    q(
        "B7",
        "B GLP-1药物选择与使用情况",
        "关于GLP-1药物起始剂量，哪一项与您的理念最相符？",
        "single",
        "返回1或2。",
        options=(
            opt(1, "希望起始剂量下较快减重，愿意忍受一定不良反应"),
            opt(2, "希望起始剂量下建立耐受、尽量减少不良反应，愿意接受较慢起效"),
        ),
    ),
    q(
        "B8",
        "B GLP-1药物选择与使用情况",
        "未曾因为体重问题到院就诊时，驱动您开启GLP-1药物治疗的主要因素有哪些？",
        "multi",
        "返回代码数组；97需给文本。",
        options=(
            opt(1, "身边亲友经验分享与推荐"),
            opt(2, "社交媒体用户经验分享与推荐"),
            opt(3, "网红、明星、企业家等知名人士的经验分享与推荐"),
            opt(4, "受到GLP-1药物广告的吸引"),
            opt(5, "因为其他合并症就诊时，医生推荐"),
            opt(6, "药房药师推荐"),
            opt(7, "互联网医生推荐/处方"),
            opt(97, "其他，请注明"),
        ),
        show_if="仅S10包含13且A9不包含1时询问。",
    ),
    q(
        "B9",
        "B GLP-1药物选择与使用情况",
        "请勾选既往使用过的GLP-1药物品牌，并填写当前使用状态和启用时间。",
        "matrix",
        "返回对象：{品牌代码: {'used': 1/2, 'status': 1仍在使用/2已停用或空, 'start_year_month': 'YYYY-MM'或空}}。",
        rows=GLP1_BRAND_OPTIONS,
        show_if="仅S10包含13或A20包含2时询问。",
    ),
    q(
        "B12",
        "B GLP-1药物选择与使用情况",
        "选择司美格鲁肽/替尔泊肽/玛仕度肽/埃诺格鲁肽时，哪些是最终决策的重要影响因素？最重要因素是什么？",
        "matrix_multi_plus_single",
        "返回对象：{品牌列代码: {'all_factors': [代码...], 'most_important': 代码}}。",
        rows=GLP1_DECISION_FACTOR_OPTIONS,
        columns=CORE_GLP1_BRAND_COLUMNS,
        show_if="仅B9使用过3/4/5/6时询问；只出示已使用药物。",
    ),
    q(
        "B13",
        "B GLP-1药物选择与使用情况",
        "选择相关GLP-1时，您从哪些信息渠道获取过产品信息？",
        "matrix_multi",
        "返回对象：{品牌列代码: [渠道代码...]}。",
        rows=INFO_CHANNEL_OPTIONS,
        columns=CORE_GLP1_BRAND_COLUMNS,
        show_if="仅B9使用过3/4/5/6时询问；只出示已使用药物。",
    ),
    q(
        "B14",
        "B GLP-1药物选择与使用情况",
        "回忆GLP-1实际使用过程中的剂量调整过程：起始剂量、维持剂量、过渡剂量及各阶段持续周数。",
        "matrix_titration",
        "返回对象：{品牌列代码: {'start_dose': 文本, 'start_weeks': 整数, 'maintenance_dose': 文本, 'maintenance_weeks': 整数, 'transition_doses': [{'dose': 文本, 'weeks': 整数}], 'total_weeks': 整数}}。",
        columns=CORE_GLP1_BRAND_COLUMNS,
        show_if="仅B9使用过3/4/5/6时询问；只出示已使用药物。",
        notes=("剂量选项按品牌不同：司美格鲁肽0.25/0.5/1/1.7/2.4mg；替尔泊肽2.5/5/10/15mg；玛仕度肽2/4/6mg；埃诺格鲁肽0.3/0.6/1.2/1.8/2.4mg。",),
    ),
    q(
        "B14d",
        "B GLP-1药物选择与使用情况",
        "估算各GLP-1使用经历中累计经历过几次漏打针。",
        "matrix_numeric",
        "返回对象：{品牌列代码: {'missed_injections': 整数}}；从未漏打填0。",
        columns=CORE_GLP1_BRAND_COLUMNS,
        show_if="仅B9使用过3/4/5/6时询问；只出示已使用药物。",
    ),
    q(
        "B10",
        "B GLP-1药物选择与使用情况",
        "既往使用过但目前已停用的GLP-1药物，停药原因分别是什么？最重要原因是什么？",
        "matrix_multi_plus_single",
        "返回对象：{已停用品牌代码: {'all_reasons': [代码...], 'most_important': 代码}}。",
        options=(
            opt(1, "减重效果不达预期", "减重疗效"),
            opt(2, "减重达平台期，体重不再下降", "减重疗效"),
            opt(3, "副作用不耐受（恶心、呕吐、腹泻、皮肤红疹等）", "安全性"),
            opt(4, "自费价格较高，经济负担较重", "经济性"),
            opt(5, "减重效果达到预期，不需要继续减重了", "其他"),
        ),
        show_if="仅B9中有目前已停用的药物时询问。",
    ),
    q(
        "B11",
        "B GLP-1药物选择与使用情况",
        "使用过至少两种GLP-1时，驱动更换药物决策的因素有哪些？",
        "matrix_multi",
        "返回对象：{换药路径: [原因代码...]}，路径示例'司美格鲁肽->替尔泊肽'。",
        options=(
            opt(1, "前序药物减重成功后体重反弹，重新开启GLP-1治疗"),
            opt(2, "前序药物减重效果不达预期，更换药物"),
            opt(3, "前序药物达到平台期，体重不再下降，更换药物"),
            opt(4, "前序药物不良反应较大，更换药物"),
            opt(5, "前序药物自费价格较高，经济负担较重，更换药物"),
            opt(6, "更换新作用机制药物，以寻求更好治疗效果"),
        ),
        show_if="仅B9使用过至少两种GLP-1时询问。",
    ),
    q(
        "X1",
        "B GLP-1药物选择与使用情况",
        "哪些GLP-1用药体验优化可以驱动您坚持使用GLP-1？最重要因素是什么？",
        "multi_plus_single",
        "返回对象：{'all_drivers': [代码...], 'most_important': 代码}。",
        options=(
            opt(1, "缓慢剂量爬坡方案，降低不良反应发生率和程度"),
            opt(2, "用药管理app/小程序，定期监督用药，避免漏针"),
            opt(3, "定期检测代谢指标，将疗效可视化"),
            opt(4, "医生建立患者打卡群，分享体验和疾病知识，互相提醒监督"),
            opt(5, "随方电话定期提醒用药，收集药物反馈"),
            opt(97, "其他，请注明"),
        ),
    ),
    q(
        "B15",
        "B GLP-1药物选择与使用情况",
        "GLP-1使用过程中，是否有中断一段时间再续用该药物的情况？次数和平均中断时长？",
        "matrix_numeric",
        "返回对象：{品牌列代码: {'interrupted': 1/2, 'times': 整数或空, 'avg_interrupt_months': 数字或空}}。",
        columns=CORE_GLP1_BRAND_COLUMNS,
        show_if="仅B9使用过3/4/5/6时询问；只出示已使用药物。",
    ),
    q(
        "B15a",
        "B GLP-1药物选择与使用情况",
        "使用该药物期间，中断再续用的原因是什么？",
        "matrix_single",
        "返回对象：{品牌列代码: 原因代码}。",
        options=(
            opt(1, "减重满意后中断，体重反弹后续用"),
            opt(2, "因不良反应较大中断，不良反应消退后续用"),
            opt(3, "因为达到平台期中断，调整状态后续用"),
            opt(4, "长期使用经济压力较大，因此阶段性使用"),
        ),
        columns=CORE_GLP1_BRAND_COLUMNS,
        show_if="仅B15中有中断再续用的药物时询问。",
    ),
    q(
        "B16",
        "B GLP-1药物选择与使用情况",
        "是否借助厂家提供的小程序作为用药记录、提醒和指南支持工具？满意度如何？最有帮助的功能是什么？",
        "matrix",
        "返回对象：{品牌列代码: {'used_tool': 1/2, 'satisfaction': 1-7或空, 'most_helpful_feature': 文本或空}}。",
        rows=(
            opt("A", "司美格鲁肽：小程序-诺和关怀"),
            opt("B", "替尔泊肽：小程序-礼来Lilly疾病支持"),
            opt("C", "玛仕度肽：小程序-自信尔美科学减重"),
        ),
        show_if="仅B9使用过3/4/5时询问；B16b仅满意度>5时填写。",
    ),
    q(
        "B17",
        "B GLP-1药物选择与使用情况",
        "使用各GLP-1药物后，体重下降了多少kg？",
        "matrix_numeric",
        "返回对象：{品牌代码: {'loss_kg': 数字}}。",
        show_if="仅S10包含13或A20包含2时询问；只出示B9使用过的药物。",
    ),
    q(
        "B18",
        "B GLP-1药物选择与使用情况",
        "停止使用各GLP-1药物后，是否经历体重反弹？若经历，反弹多少kg？",
        "matrix_numeric",
        "返回对象：{停用品牌代码: {'rebounded': 1/2, 'rebound_kg': 数字或空}}。",
        show_if="仅B9中有目前已停用药物时询问。",
    ),
    q(
        "B19",
        "B GLP-1药物选择与使用情况",
        "结合实际使用体验，对使用过的GLP-1药物在各维度表现的满意度打分。",
        "matrix_rating_1_7",
        "返回对象：{品牌列代码: {维度代码: 1-7评分}}。",
        rows=GLP1_EVALUATION_ROWS,
        columns=CORE_GLP1_BRAND_COLUMNS,
        show_if="仅B9使用过3/4/5/6时询问；只出示已使用药物。",
        validations=("总体满意度需介于单项最高分和最低分之间；避免纵向连续5项相同。",),
    ),
    q(
        "B20",
        "B GLP-1药物购买渠道",
        "初次购买各GLP-1药物的渠道分别是什么？",
        "matrix_single",
        "返回对象：{品牌列代码: 渠道代码}。",
        rows=PURCHASE_CHANNEL_OPTIONS,
        columns=CORE_GLP1_BRAND_COLUMNS,
        show_if="仅B9使用过3/4/5/6时询问；只出示已使用药物。",
    ),
    q(
        "B20a",
        "B GLP-1药物购买渠道",
        "初次通过电商购买GLP-1时，电商平台分别是什么？",
        "matrix_single",
        "返回对象：{品牌列代码: 平台代码}。",
        rows=ECOMMERCE_PLATFORM_OPTIONS,
        columns=CORE_GLP1_BRAND_COLUMNS,
        show_if="仅出示B20=2（电商）的药物。",
    ),
    q(
        "B21",
        "B GLP-1药物购买渠道",
        "在电商平台初次购买GLP-1前，对自身健康情况做了哪些评估？",
        "matrix_multi",
        "返回对象：{品牌列代码: [评估项代码...]}；99与其他互斥。",
        rows=(
            opt(1, "身体质量指数BMI"),
            opt(2, "血糖"),
            opt(3, "血脂"),
            opt(4, "甲状腺风险"),
            opt(5, "胰腺病史"),
            opt(6, "胃肠道状况"),
            opt(7, "肝肾功能"),
            opt(8, "阻塞性睡眠呼吸暂停情况", note="仅替尔泊肽列出"),
            opt(99, "以上健康情况均未评估", note="与其他互斥"),
        ),
        columns=CORE_GLP1_BRAND_COLUMNS,
        show_if="仅出示B20=2（电商）的药物。",
    ),
    q(
        "B22",
        "B GLP-1药物购买渠道",
        "在电商平台初次购买GLP-1时，处方由谁开具？",
        "matrix_single",
        "返回对象：{品牌列代码: 处方代码}。",
        rows=(
            opt(1, "上传院内医生开具的处方至电商平台"),
            opt(2, "在电商平台在线问诊，在线处方"),
        ),
        columns=CORE_GLP1_BRAND_COLUMNS,
        show_if="仅出示B20=2（电商）的药物。",
    ),
    q(
        "B23",
        "B GLP-1药物购买渠道",
        "后续续药各GLP-1药物的渠道有哪些？",
        "matrix_multi",
        "返回对象：{品牌列代码: [渠道代码...]}。",
        rows=PURCHASE_CHANNEL_OPTIONS,
        columns=CORE_GLP1_BRAND_COLUMNS,
        show_if="仅B9使用过3/4/5/6时询问；只出示已使用药物。",
    ),
    q(
        "B23a",
        "B GLP-1药物购买渠道",
        "后续通过电商续药GLP-1时，电商平台有哪些？",
        "matrix_multi",
        "返回对象：{品牌列代码: [平台代码...]}。",
        rows=ECOMMERCE_PLATFORM_OPTIONS,
        columns=CORE_GLP1_BRAND_COLUMNS,
        show_if="仅出示B23包含2（电商）的药物。",
    ),
    q(
        "B24",
        "B GLP-1停药患者序贯意愿测试",
        "是否可以接受再次使用其他品牌GLP-1作为减重治疗方案？",
        "single",
        "返回1或2。",
        options=YES_NO,
        show_if="仅B9所有使用过药物状态均为目前已停用时询问。",
    ),
    q(
        "B24a",
        "B GLP-1停药患者序贯意愿测试",
        "希望接受以下哪个未使用过的GLP-1作为减重治疗方案？",
        "single",
        "返回一个代码；98表示暂未想好。",
        options=(
            opt(1, "司美格鲁肽（诺和盈、诺和泰）"),
            opt(2, "替尔泊肽（穆峰达）"),
            opt(3, "玛仕度肽（信尔美）"),
            opt(4, "埃诺格鲁肽（先维盈、先颐达）"),
            opt(98, "暂时还未想好希望再次接受的GLP-1治疗方案"),
        ),
        show_if="仅B24=1时询问；只出示B9未使用过的药物。",
    ),
    q(
        "B24b",
        "B GLP-1停药患者序贯意愿测试",
        "更希望接受B24a所选GLP-1作为后续减重治疗方案的原因有哪些？",
        "multi",
        "返回代码数组；97需给文本。",
        options=(
            opt(1, "希望可以尝试其他作用机制的GLP-1药物"),
            opt(2, "身边亲友经验分享与推荐"),
            opt(3, "社交媒体用户经验分享与推荐"),
            opt(4, "网红、明星、企业家等知名人士的经验分享与推荐"),
            opt(5, "受到该品牌推广广告/宣传数据中减重疗效的吸引"),
            opt(6, "受到该品牌推广广告/宣传数据中安全性的吸引"),
            opt(7, "受到该品牌推广广告/宣传数据中其他代谢获益吸引"),
            opt(97, "其他，请注明"),
        ),
        show_if="仅B24a=1/2/3/4时询问。",
    ),
    q(
        "C1",
        "C 新产品测试",
        "阅读产品X、产品A、产品B、产品C信息后，对各药物在各维度上的表现满意度和总体满意度分别打分。",
        "matrix_rating_1_7",
        "返回对象：{产品代码: {维度代码: 1-7评分}}。",
        rows=(
            opt(1, "可治疗疾病布局"),
            opt(2, "使用方式"),
            opt(3, "减重疗效"),
            opt(4, "代谢相关获益"),
            opt(5, "安全性/耐受性"),
            opt(6, "总体满意度"),
        ),
        columns=PRODUCT_COLUMNS,
        notes=("回答前必须阅读C部分产品示卡信息；评分必须基于示卡中的机制、适应症、给药方式、疗效、代谢获益和安全性。",),
    ),
    q(
        "C2",
        "C 新产品测试",
        "阅读产品信息后，在不考虑价格的情况下，您对产品X的使用意愿如何？",
        "rating_0_10",
        "返回0-10整数。",
        options=WILLINGNESS_0_10,
        notes=("0表示不会，5表示可能会，10表示一定会；必须基于C部分产品示卡中的产品X信息回答。",),
    ),
    q(
        "C3",
        "C 新产品测试",
        "若对产品X使用意愿不足8分，哪些因素导致犹豫？并选出最主要的三个原因排序。",
        "multi_plus_rank",
        "返回对象：{'all_reasons': [代码...], 'top3_rank': {代码: 1/2/3}}。",
        options=(
            opt(1, "爬坡剂量太多，前期频繁调整，达到维持剂量周期较长", note="仅B6=2时出示"),
            opt(2, "任何不良反应发生率较高"),
            opt(3, "缺少停药后反弹情况的相关数据"),
            opt(4, "缺少起效速度的相关数据"),
            opt(5, "对目前使用的GLP-1药物较满意，暂不考虑更换", note="仅B9有仍在使用药物时出示"),
            opt(6, "没有2型糖尿病适应症", note="仅S8=2糖尿病时出示"),
            opt(7, "对GLP-1用于减重的效果失去信心，不再考虑使用", note="仅使用过GLP-1时出示"),
        ),
        show_if="仅C2<8时询问。",
        notes=("犹豫原因应来自产品X示卡信息与persona自身顾虑的结合。",),
    ),
    q(
        "C4_C5",
        "C 商品名测试",
        "对各GLP-1药物商品名的易读性和好记程度打分。",
        "matrix_rating_1_7",
        "返回对象：{商品名代码: {'readability': 1-7, 'memorability': 1-7}}。",
        rows=(
            opt(1, "欧双逸"),
            opt(2, "飒维妥"),
            opt(3, "飒维安"),
            opt(4, "欧双悦"),
            opt(5, "飒维坦"),
            opt(6, "飒维悦"),
        ),
        notes=("原题干写5个商品名，但表格实际列出6个；模板按表格6个商品名处理。",),
    ),
    q(
        "C6",
        "C 商品名测试",
        "评价各商品名与'重新定义代谢健康，从而改变患者的生活方式、遇见更好的未来'产品理念的相关程度。",
        "matrix_rating_1_7",
        "返回对象：{商品名代码: 1-7评分}。",
        rows=(
            opt(1, "欧双逸"),
            opt(2, "飒维妥"),
            opt(3, "飒维安"),
            opt(4, "欧双悦"),
            opt(5, "飒维坦"),
            opt(6, "飒维悦"),
        ),
        notes=("原题干写5个商品名，但表格实际列出6个；模板按表格6个商品名处理。",),
    ),
    q(
        "C7",
        "C 商品名测试",
        "评价各商品名与'助力患者迈上通往健康的道路，自由前行'产品理念的相关程度。",
        "matrix_rating_1_7",
        "返回对象：{商品名代码: 1-7评分}。",
        rows=(
            opt(1, "欧双逸"),
            opt(2, "飒维妥"),
            opt(3, "飒维安"),
            opt(4, "欧双悦"),
            opt(5, "飒维坦"),
            opt(6, "飒维悦"),
        ),
        notes=("原题干写5个商品名，但表格实际列出6个；模板按表格6个商品名处理。",),
    ),
    q(
        "D1",
        "D 受访者基本情况",
        "下列哪项最能描述您本人现在的工作状态？",
        "single",
        "返回一个代码。",
        options=(
            opt(1, "全职"),
            opt(2, "兼职"),
            opt(3, "无工作"),
            opt(4, "退休"),
            opt(5, "学生"),
            opt(97, "其他，请注明"),
        ),
    ),
    q(
        "D2",
        "D 受访者基本情况",
        "请问您本人目前的职业是什么？兼职被访者请选择当前最主要工作。",
        "single",
        "返回一个代码；97需给文本。",
        options=(
            opt(1, "公务员/国有企业事业编制"),
            opt(2, "军人/部队工作"),
            opt(3, "非办公室工作者：建筑工人、技术工人等"),
            opt(4, "非办公室工作者：售货员、保洁员、服务员等"),
            opt(5, "专业人员：老师、科研人员、律师、工程师等"),
            opt(6, "一般办公室职员"),
            opt(7, "中高层管理人员"),
            opt(8, "高层管理人员"),
            opt(9, "企业主"),
            opt(10, "私营业主（5位或以上雇员）"),
            opt(11, "个体户（5位以下雇员）"),
            opt(12, "农民"),
            opt(97, "其他，请注明"),
        ),
        show_if="仅D1=1/2时询问。",
    ),
    q(
        "D3",
        "D 受访者基本情况",
        "请选择与您的工作性质最相符的描述。",
        "multi",
        "返回代码数组。",
        options=(
            opt(1, "体力劳动型：持续站立、搬运重物或大量走动"),
            opt(2, "静态办公型：持续久坐，极少走动"),
            opt(3, "外勤奔波型：频繁出差，饮食不规律，依赖外卖或快餐"),
            opt(4, "商务应酬型：频繁饮酒、应酬"),
            opt(5, "轮班作业型：工作时间不固定，经常熬夜、倒班或昼夜颠倒"),
            opt(6, "形象需求型：工作对个人外在形象、气质仪态有明确要求"),
        ),
        validations=("选项1和2不能同时选择；2和3不能同时选择。",),
    ),
    q(
        "D4",
        "D 受访者基本情况",
        "请问您的婚姻状况如何？",
        "single",
        "返回一个代码。",
        options=(
            opt(1, "未婚"),
            opt(2, "已婚"),
            opt(3, "离婚"),
            opt(4, "丧偶"),
        ),
    ),
    q(
        "D5",
        "D 受访者基本情况",
        "请问您是否有子女？共有几个子女？",
        "single",
        "返回一个代码。",
        options=(
            opt(1, "没有子女"),
            opt(2, "有1个子女"),
            opt(3, "有2个子女"),
            opt(4, "有3个或以上子女"),
        ),
        show_if="仅D4=2/3/4时询问。",
    ),
    q(
        "D6",
        "D 受访者基本情况",
        "日常生活中，您主要需要照顾哪些家庭成员？",
        "single",
        "返回一个代码。",
        options=(
            opt(1, "主要照顾小孩"),
            opt(2, "主要照顾老人"),
            opt(3, "既要照顾小孩，又要照顾老人"),
            opt(4, "既不照顾小孩，也不照顾老人"),
        ),
    ),
    q(
        "D7",
        "D 受访者基本情况",
        "请对以下健康理念和身体状态表述的认同度打分。",
        "matrix_rating_1_7",
        "返回对象：{表述代码: 1-7评分}。",
        rows=(
            opt(1, "我减肥是为了让身体更健康"),
            opt(2, "我减肥是为了让身体感到舒适"),
            opt(3, "在当前人生阶段，我发现维持健康的体重越来越困难了"),
            opt(4, "在当前人生阶段，我发现减肥越来越困难了"),
            opt(5, "我渴望做更多有意义的事情，但当前精力水平无法支持"),
            opt(6, "我强烈渴望保持身体健康"),
            opt(7, "我强烈渴望获得强健的身材"),
            opt(8, "我强烈渴望获得敏锐的思维"),
            opt(9, "我会积极主动地进行健康管理"),
            opt(10, "我会积极主动地提升自我"),
        ),
    ),
    q(
        "D8",
        "D 受访者基本情况",
        "请对以下减重理念的认同度打分。",
        "matrix_rating_1_7",
        "返回对象：{理念代码: 1-7评分}。",
        rows=(
            opt(1, "身边的人理解我的身体状况、认可我减重的努力，是我坚持的重要动力"),
            opt(2, "减肥行动力取决于人生阶段对健康管理、形象管理需要的紧迫程度"),
            opt(3, "理想减重体验应高效、不花太多精力、不影响正常生活节奏"),
            opt(4, "可持续、低成本、无偏见的电子支持工具会使减重事半功倍"),
        ),
    ),
    q(
        "D9",
        "D 受访者基本情况",
        "想象一个理想的微信支持工具，以下哪种功能对您最有吸引力？",
        "single",
        "返回一个代码。",
        options=(
            opt(1, "智能提醒：温柔提醒用药、喝水或吃得更健康"),
            opt(2, "无压记录：拍照自动识别食物和热量，无需手动输入"),
            opt(3, "正向反馈：达成小目标时收到鼓励，而不是没达标时被批评"),
            opt(4, "专家答疑：随时向药师、营养师提问并快速得到专业解答"),
        ),
        show_if="仅D8-4>5时询问。",
    ),
)


OBESITY_PATIENT_SYSTEM_PROMPT = (
    "你正在模拟一位中国体重管理/肥胖患者市场调研受访者。"
    "请只依据给定的种子信息和数字个体画像作答，不要编造与画像冲突的事实。"
    "这是一份市场研究问卷，不是医学建议；你要像真实受访者一样回答编码题。"
    "必须遵守题目显示条件、互斥规则和前后逻辑。"
    "单选题返回一个代码，多选题返回代码数组，排序题返回代码到名次的对象，矩阵题返回嵌套对象，数值题返回合理数值。"
    "不适用或未显示的题目请返回空字符串或空对象。"
    "只输出JSON，不要解释。"
)


def _format_option(option: Option) -> str:
    group = f"[{option.group}] " if option.group else ""
    note = f"（{option.note}）" if option.note else ""
    return f"{option.code}. {group}{option.label}{note}"


def _format_options(title: str, options: Sequence[Option]) -> list[str]:
    if not options:
        return []
    lines = [f"{title}："]
    lines.extend(f"  - {_format_option(option)}" for option in options)
    return lines


def format_question_for_prompt(spec: QuestionSpec) -> str:
    lines = [
        f"{spec.qid} | {spec.section} | {spec.response_type}",
        f"题目：{spec.stem}",
        f"答题格式：{spec.answer_format}",
    ]
    if spec.show_if:
        lines.append(f"显示条件：{spec.show_if}")
    lines.extend(_format_options("选项", spec.options))
    lines.extend(_format_options("矩阵行/评价项", spec.rows))
    lines.extend(_format_options("矩阵列/品牌或产品", spec.columns))
    if spec.validations:
        lines.append("校验/逻辑：")
        lines.extend(f"  - {item}" for item in spec.validations)
    if spec.notes:
        lines.append("备注：")
        lines.extend(f"  - {item}" for item in spec.notes)
    return "\n".join(lines)


def format_product_card_context(product_card: Mapping[str, Mapping[str, str]] | None = None) -> str:
    source = product_card or PRODUCT_CARD
    lines = [
        "C部分产品示卡（所有受访者在回答C1-C7前必须阅读）：",
        "这张示卡用于模拟访谈中展示给受访者的信息输入。请先让persona理解四个产品的核心差异：",
        "产品X、产品C都是GLP-1R/GCGR双靶点，强调GLP-1带来的食欲控制之外，也可能通过胰高糖素相关机制影响能量消耗、脂肪代谢和肝脏脂肪；",
        "产品A是GLP-1R/GIP双靶点，更容易被理解为兼顾减重与糖代谢控制；产品B是传统GLP-1R激动剂，机制更单一但临床信息较清晰。",
        "四个产品均为每周一次皮下注射，差异主要体现在剂量爬坡复杂度、长期体重管理与MASH/2型糖尿病布局、全球或中国减重数据、代谢指标改善幅度以及不良反应发生率。",
    ]
    for product_name, attributes in source.items():
        lines.append(f"- {product_name}")
        for key, value in attributes.items():
            lines.append(f"  - {key}: {value}")
    return "\n".join(lines)


def questionnaire_to_prompt_text(
    *,
    include_screening: bool = True,
    include_analysis_summary: bool = True,
) -> str:
    specs = (
        QUESTIONNAIRE
        if include_screening
        else tuple(spec for spec in QUESTIONNAIRE if spec.section != "甄别问卷" and spec.qid != "CONSENT")
    )
    sections: list[str] = []
    if include_analysis_summary:
        sections.append("问卷结构分析：\n" + "\n".join(f"- {item}" for item in QUESTIONNAIRE_ANALYSIS))
    sections.append(format_product_card_context())
    sections.append("题目清单：\n" + "\n\n".join(format_question_for_prompt(spec) for spec in specs))
    return "\n\n".join(sections)


def expected_answer_shape(
    *,
    include_screening: bool = True,
) -> dict[str, str]:
    specs = (
        QUESTIONNAIRE
        if include_screening
        else tuple(spec for spec in QUESTIONNAIRE if spec.section != "甄别问卷" and spec.qid != "CONSENT")
    )
    return {spec.qid: spec.answer_format for spec in specs}


def build_obesity_patient_questionnaire_user_prompt(
    individual_id: str,
    seed_context: str,
    profile_text: str,
    *,
    include_screening: bool = True,
) -> str:
    questionnaire_text = questionnaire_to_prompt_text(include_screening=include_screening)
    return (
        f"受访者ID：{individual_id}\n\n"
        f"种子信息：\n{seed_context}\n\n"
        f"数字个体画像：\n{profile_text}\n\n"
        "请以该受访者身份回答下面的中文问卷。\n"
        "输出要求：\n"
        "- 返回JSON对象，顶层只包含一个键：answers。\n"
        "- answers中的键必须使用题目ID。\n"
        "- 对于不符合显示条件的题目，值填空字符串、空数组或空对象。\n"
        "- 保持BMI、合并症、减重经历、就医路径、GLP-1品牌使用、购药渠道、停药/换药原因前后一致。\n"
        "- 数值题要合理：减重时长、目标体重、花费、体重下降、反弹、剂量持续周数等必须符合画像和常识。\n"
        "- 评分题允许差异化，不要机械地全部给同一个分数。\n\n"
        f"{questionnaire_text}\n\n"
        "请仅输出JSON。"
    )


if __name__ == "__main__":
    print(questionnaire_to_prompt_text())
