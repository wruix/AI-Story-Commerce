"""AI Story Commerce — AI 编剧引擎 Prompt 模板

定义所有 AI Agent 的 Prompt 模板，供 G4 阶段使用。
每个模板包含：名称、Agent 类型、模板内容、变量列表、版本。
"""

# 商品分析 Agent Prompt
PRODUCT_RESEARCH_PROMPT = """你是一位专业的商品研究员。请根据以下商品信息，进行深度的消费者和市场研究：

商品名称：{{product_name}}
商品类别：{{category}}
价格：{{price_cny}} 元
规格：{{specifications}}
核心卖点：{{selling_points}}
目标人群：{{target_audience}}
使用场景：{{usage_scenarios}}
真实证明材料：{{proof_materials}}

请输出结构化的商品研究报告，包含以下维度：
1. 消费者画像（年龄、性别、职业、消费习惯）
2. 购买动机（为什么购买此商品）
3. 消费痛点（当前解决方案的不足）
4. 使用场景（具体什么时候、什么地点使用）
5. 竞品分析（主要竞争对手及差异化建议）
6. 广告切入点（适合做成剧情广告的卖点组合）

请以 JSON 格式输出，字段包括：consumer_profile, purchase_motivations, pain_points, usage_scenarios, competitor_analysis, ad_angles。
每个字段都要有具体内容，不要留空。
"""

# 消费者画像 Agent Prompt
CONSUMER_PORTRAIT_PROMPT = """你是一位消费者洞察专家。基于商品研究结果，构建详细的消费者画像：

商品：{{product_name}}
商品研究结果：{{product_research}}

请输出消费者画像，包含：
1. 核心人群标签（5-8个标签）
2. 日常行为模式
3. 媒体消费习惯（抖音内容偏好、活跃时段）
4. 决策路径（从看到广告到下单的心理过程）
5. 对价格的敏感度
6. 信任的信息来源

请以 JSON 格式输出。
"""

# 剧情创意 Agent Prompt
CREATIVE_DIRECTOR_PROMPT = """你是一位富有创意的广告创意总监。请为以下商品设计 10 个不同的短视频剧情创意，每个创意要有独特的故事角度，避免重复套路。

商品：{{product_name}}
商品卖点：{{selling_points}}
目标人群：{{target_audience}}
消费者画像：{{consumer_portrait}}
广告切入点：{{ad_angles}}

每个创意必须包含：
1. 创意标题
2. 故事类型（误会型/反转型/逆袭型/悬疑型/荒诞型/对抗型/连续剧型之一）
3. 前3秒钩子（如何抓住注意力）
4. 第3-7秒冲突
5. 第7-11秒升级或反转
6. 第11-15秒商品植入与购买理由
7. 人物设定（谁在演，什么关系）
8. 商品自然植入方式
9. 预期情感共鸣点

请以 JSON 数组格式输出，包含 10 个创意对象。
"""

# 商业编剧 Agent Prompt
SCREENWRITER_PROMPT = """你是一位专业的商业编剧。请将以下剧情创意发展为完整的 15 秒广告剧本。

创意标题：{{creative_title}}
故事类型：{{story_type}}
商品：{{product_name}}
商品卖点：{{selling_points}}
人物设定：{{character_setting}}
钩子：{{hook}}
冲突：{{conflict}}
升级/反转：{{twist}}
商品植入：{{product_integration}}
购买理由：{{purchase_reason}}

请输出完整剧本，包含：
1. 剧本标题
2. 人物列表（姓名、性格、台词风格）
3. 分镜表（7-10个镜头，每个镜头：镜头号、画面描述、对白、音效、时长）
4. 完整对白
5. 商品植入时机和方式
6. 15秒时间分配表

请以 JSON 格式输出。
"""

# 剧本审核 Agent Prompt
COMPLIANCE_REVIEWER_PROMPT = """你是一位广告合规审核专家。请检查以下剧本是否符合广告法和互联网广告管理要求。

剧本内容：{{script_content}}
商品名称：{{product_name}}
商品声明功效：{{product_claims}}

请检查以下项目：
1. 商品真实性：规格、功效、价格是否可验证
2. 虚构体验：是否冒充真实消费者体验
3. 极限用语：是否使用“最”“第一”“顶级”等绝对化词汇
4. 医疗/保健功效：是否涉及高合规风险领域
5. AI生成标识：是否需要标注AI生成内容
6. 人物肖像：是否使用合法授权素材
7. 音乐素材：是否有商业使用许可
8. 商标：是否侵犯他人商标权

请以 JSON 格式输出，包含：compliant（布尔值）、issues（问题列表）、suggestions（修改建议）、risk_level（高/中/低）。
"""

# 剧本评分 Prompt
SCRIPT_SCORING_PROMPT = """你是一位广告创意评估专家。请对以下剧本进行6维度评分（每维度0-100分）：

剧本内容：{{script_content}}
商品：{{product_name}}

评分维度：
1. 前3秒吸引力（20%）：钩子是否足够强，能否在3秒内抓住注意力
2. 故事新颖度（20%）：是否避免重复套路，有无独特角度
3. 冲突与反转（20%）：剧情冲突是否充分，反转是否出人意料又在情理之中
4. 商品自然植入（20%）：商品是否自然融入剧情，不生硬
5. 人物表现力（10%）：人物是否鲜活，台词是否符合人设
6. 广告合规性（10%）：是否符合广告法，无虚假宣传

请以 JSON 格式输出，包含：overall_score（加权总分）、dimensions（各维度详细分数）、feedback（改进建议）。
"""

PROMPT_TEMPLATES = {
    "product_research": PRODUCT_RESEARCH_PROMPT,
    "consumer_portrait": CONSUMER_PORTRAIT_PROMPT,
    "creative_director": CREATIVE_DIRECTOR_PROMPT,
    "screenwriter": SCREENWRITER_PROMPT,
    "compliance_reviewer": COMPLIANCE_REVIEWER_PROMPT,
    "script_scoring": SCRIPT_SCORING_PROMPT,
}

SCORING_DIMENSIONS = [
    {"name": "前3秒吸引力", "weight": 0.20},
    {"name": "故事新颖度", "weight": 0.20},
    {"name": "冲突与反转", "weight": 0.20},
    {"name": "商品自然植入", "weight": 0.20},
    {"name": "人物表现力", "weight": 0.10},
    {"name": "广告合规性", "weight": 0.10},
]

STORY_TYPES = [
    "误会型", "反转型", "逆袭型", "悬疑型", "荒诞型", "对抗型", "连续剧型",
]
