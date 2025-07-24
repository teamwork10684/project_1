import ollama
from module.aifilter.aifilter import filter_markdown
import json as pyjson
import random
import requests
import os
import yaml
import openai
# 读取config.yaml中的question_generate配置
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.yaml')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    _full_config = yaml.safe_load(f)
    QUESTION_GEN_CONFIG = _full_config.get('question_generate', {})
    OLLAMA_MODEL_NAME = QUESTION_GEN_CONFIG.get('ollama_model_name', 'deepseek-r1:7b')
    USE_API = QUESTION_GEN_CONFIG.get('use_api', False)
    API_CONFIG = QUESTION_GEN_CONFIG.get('api', {})


def generate_question_by_ollama(text, model=OLLAMA_MODEL_NAME):
    """
    调用ollama根据文本生成一道高质量的单项选择题。
    :param text: 原始文本内容
    :param model: ollama模型名
    :return: (prompt, question, options, answer)
    :raises: Exception if AI返回格式不正确或服务异常
    """
    prompt = (
        """
        # 高质量选择题生成专家提示词
        ## 角色定位
        你是一位拥有5年以上教育评估经验的试题生成专家，擅长从文本中提取关键信息并转化为有效评估题目。你的任务是基于提供的文本内容，生成高质量、诊断性强的四选一选择题，帮助全面评估读者对文本的理解程度。
        ## 任务描述
        请根据以下提供的文本内容，生成**一个**四选一选择题。题目应能有效测试读者对文本关键信息的理解和应用能力，而非简单记忆。
        ## 内容质量要求
        ### 题目设计标准
        1. **难度控制** ：选项应具有迷惑性，避免出现明显错误选项；正确答案不应过于明显或过于隐晦
        2. **题干要求** ：题干中需要避免出现“文中提到”、“根据文本”等类似字样。
        ### 选项设计规范
        1. 题目必须有且仅有4个选项(A/B/C/D)
        2. 选项长度应保持相近，避免通过长度差异暗示正确答案
        3. 错误选项应具有似真性，基于文本内容可能产生的误解设计
        4. 避免使用"以上都对"、"以上都不对"等非特异性选项
        5. 选项内容应相互独立，不包含重叠或包含关系
        6. 所有选项语法结构应保持一致，与问题形成合理搭配
        ### 答案准确性要求
        1. 正确答案必须100%来源于文本，确保绝对准确
        2. 题目只能有一个明确正确的答案
        ## 格式输出规范
        1. **唯一输出内容** ：仅返回一个标准JSON数据，不包含任何前置说明、后置解释、格式标记或注释
        2. **JSON结构** ：
        ```
        {
            "question": "完整的问题描述，以问号结尾",
            "options": ["选项A内容", "选项B内容", "选项C内容", "选项D内容"],
            "answer": "A"  // 只能是单个大写字母(A/B/C/D)
        }
        ```
        3. **格式约束** ：
        * 严格使用双引号，不使用单引号
        * 确保JSON语法完全正确，可直接解析
        * 问题和选项中不包含任何Markdown格式
        * 选项文本不包含序号(A./B.等)
        ## 示例
        ### 正确示例（仅为示例，非文本中内容）
        ```
        {
            "question": "光合作用的主要产物是什么？",
            "options": ["氧气和葡萄糖", "二氧化碳和水", "氮气和氧气", "氢气和氧气"],
            "answer": "A"
        }
        ```
        ### 错误示例（请勿模仿）
        ```
        // 这是错误示例，包含了注释和多余文本
        {
            "题目": "光合作用的主要产物？",  // 使用了错误的字段名
            "选项": ["氧气", "二氧化碳", "水"],  // 选项数量不足
            "正确答案": "氧气"  // 使用了错误的字段名和值格式
        }
        ```
        ## 执行流程
        1. 首先理解全文，抓住核心要点
        2. 为每个题目设计4个选项，其中1个正确答案，3个具有迷惑性的错误选项
        3. 检查题目确保符合上述质量和格式要求
        4. 仅输出最终JSON数组，不包含任何其他内容
        请根据以上要求，基于以下文本内容生成**一道**四选一选择题："""+
        f'{text}'
    )
    print("开始调用ollama出题")
    response = ollama.generate(
        model=model,
        prompt=prompt,
        stream=False,
        think=False
    )
    print("ollama出题完成")
    response_text = response.get('response', '')
    response_text = filter_markdown(response_text)
    data = pyjson.loads(response_text)
    question = data.get('question')
    options = data.get('options')
    answer = data.get('answer')
    if not question or not isinstance(options, list) or len(options) != 4 or answer not in ['A', 'B', 'C', 'D']:
        print("AI出题错误")
        raise ValueError('AI返回格式不正确')
    # 随机打乱选项并更新答案
    option_map = list(zip(['A', 'B', 'C', 'D'], options))
    random.shuffle(option_map)
    shuffled_options = [opt for _, opt in option_map]
    original_answer_content = options[ord(answer) - ord('A')]
    for idx, (_, opt) in enumerate(option_map):
        if opt == original_answer_content:
            new_answer = chr(ord('A') + idx)
            break
    else:
        new_answer = None
    return prompt, question, shuffled_options, new_answer

def generate_question_by_api(text, api_config):
    """
    使用API方式（如OpenAI）根据文本生成一道高质量的单项选择题。
    :param text: 原始文本内容
    :param api_config: dict，包含api_key, model_name, base_url, temperature, max_tokens, top_p等
    :return: (prompt, question, options, answer)
    :raises: Exception if API返回格式不正确或服务异常
    """
    prompt = (
        """
        # 高质量选择题生成专家提示词
        ## 角色定位
        你是一位拥有5年以上教育评估经验的试题生成专家，擅长从文本中提取关键信息并转化为有效评估题目。你的任务是基于提供的文本内容，生成高质量、诊断性强的四选一选择题，帮助全面评估读者对文本的理解程度。
        ## 任务描述
        请根据以下提供的文本内容，生成**一个**四选一选择题。题目应能有效测试读者对文本关键信息的理解和应用能力，而非简单记忆。
        ## 内容质量要求
        ### 题目设计标准
        1. **难度控制** ：选项应具有迷惑性，避免出现明显错误选项；正确答案不应过于明显或过于隐晦
        2. **题干要求** ：题干中需要避免出现“文中提到”、“根据文本”等类似字样。
        ### 选项设计规范
        1. 题目必须有且仅有4个选项(A/B/C/D)
        2. 选项长度应保持相近，避免通过长度差异暗示正确答案
        3. 错误选项应具有似真性，基于文本内容可能产生的误解设计
        4. 避免使用"以上都对"、"以上都不对"等非特异性选项
        5. 选项内容应相互独立，不包含重叠或包含关系
        6. 所有选项语法结构应保持一致，与问题形成合理搭配
        ### 答案准确性要求
        1. 正确答案必须100%来源于文本，确保绝对准确
        2. 题目只能有一个明确正确的答案
        ## 格式输出规范
        1. **唯一输出内容** ：仅返回一个标准JSON数据，不包含任何前置说明、后置解释、格式标记或注释
        2. **JSON结构** ：
        ```
        {
            "question": "完整的问题描述，以问号结尾",
            "options": ["选项A内容", "选项B内容", "选项C内容", "选项D内容"],
            "answer": "A"  // 只能是单个大写字母(A/B/C/D)
        }
        ```
        3. **格式约束** ：
        * 严格使用双引号，不使用单引号
        * 确保JSON语法完全正确，可直接解析
        * 问题和选项中不包含任何Markdown格式
        * 选项文本不包含序号(A./B.等)
        ## 示例
        ### 正确示例（仅为示例，非文本中内容）
        ```
        {
            "question": "光合作用的主要产物是什么？",
            "options": ["氧气和葡萄糖", "二氧化碳和水", "氮气和氧气", "氢气和氧气"],
            "answer": "A"
        }
        ```
        ### 错误示例（请勿模仿）
        ```
        // 这是错误示例，包含了注释和多余文本
        {
            "题目": "光合作用的主要产物？",  // 使用了错误的字段名
            "选项": ["氧气", "二氧化碳", "水"],  // 选项数量不足
            "正确答案": "氧气"  // 使用了错误的字段名和值格式
        }
        ```
        ## 执行流程
        1. 首先理解全文，抓住核心要点
        2. 为每个题目设计4个选项，其中1个正确答案，3个具有迷惑性的错误选项
        3. 检查题目确保符合上述质量和格式要求
        4. 仅输出最终JSON数组，不包含任何其他内容
        请根据以上要求，基于以下文本内容生成**一道**四选一选择题："""+
        f'{text}'
    )
    client = openai.OpenAI(
        api_key=api_config.get('api_key', ''),
        base_url=api_config.get('base_url', ''),
    )
    print("开始调用API出题")
    completion=client.chat.completions.create(
        model=api_config.get('model_name', 'qwen-max'),
        messages=[
            {"role": "system", "content": "你是一位拥有5年以上教育评估经验的试题生成专家，擅长从文本中提取关键信息并转化为有效评估题目。你的任务是基于提供的文本内容，生成高质量、诊断性强的四选一选择题，帮助全面评估读者对文本的理解程度。"},
            {"role": "user", "content": prompt}
        ],
    )
    print("API出题完成")
    response_text = completion.choices[0].message.content
    response_text = filter_markdown(response_text)
    data = pyjson.loads(response_text)
    question = data.get('question')
    options = data.get('options')
    answer = data.get('answer')
    if not question or not isinstance(options, list) or len(options) != 4 or answer not in ['A', 'B', 'C', 'D']:
        raise ValueError('API返回格式不正确')
    # 随机打乱选项并更新答案
    option_map = list(zip(['A', 'B', 'C', 'D'], options))
    random.shuffle(option_map)
    shuffled_options = [opt for _, opt in option_map]
    original_answer_content = options[ord(answer) - ord('A')]
    for idx, (_, opt) in enumerate(option_map):
        if opt == original_answer_content:
            new_answer = chr(ord('A') + idx)
            break
    else:
        new_answer = None
    return prompt, question, shuffled_options, new_answer

def generate_question(text, is_batch=False,count=1):
    """
    统一入口，根据use_api决定调用ollama或api方式。
    :param text: 原始文本内容
    :param use_api: 是否使用API方式
    :param api_config: API配置
    :param model: ollama模型名
    :return: (prompt, question, options, answer)
    """
    if USE_API:
        if not API_CONFIG:
            raise ValueError('API配置不能为空')
        else:
            if is_batch:
                return generate_question_by_api_batch(text,count,API_CONFIG)
            else:
                return generate_question_by_api(text, API_CONFIG)
    else:
        if not OLLAMA_MODEL_NAME:
            raise ValueError('ollama模型名不能为空')
        else:
            if is_batch:
                return generate_question_by_ollama_batch(text,count,OLLAMA_MODEL_NAME)
            else:
                return generate_question_by_ollama(text, OLLAMA_MODEL_NAME)

def generate_question_by_api_batch(text_list, count=1, api_config=API_CONFIG):
    """
    批量方式，根据text_list拼接为长文本，调用API生成题目。
    :param text_list: 文本列表，每个元素为一页内容
    :param count: 生成题目数量
    :param api_config: API配置
    :return: [(prompt, question, options, answer), ...]
    """
    if not isinstance(text_list, list) or not text_list:
        raise ValueError('text_list必须为非空列表')
    # 拼接文本，每页加页码
    merged_text = "\n".join([
        f"【第{i+1}页开始】\n{text}\n【第{i+1}页结束】" for i, text in enumerate(text_list)
    ])
    prompt = (
        """
        # 高质量选择题生成专家提示词
        ## 角色定位
        你是一位拥有5年以上教育评估经验的试题生成专家，擅长从文本中提取关键信息并转化为有效评估题目。你的任务是基于提供的文本内容，生成高质量、诊断性强的四选一选择题，帮助全面评估读者对文本的理解程度。
        ## 任务描述
        请根据以下提供的文本内容，生成**"""+
        f'{count}'+
        """道**四选一选择题。所有题目必须直接来源于文本内容，不得加入任何外部知识。题目应能有效测试读者对文本关键信息的理解和应用能力，而非简单记忆。
        ## 内容质量要求
        ### 题目设计标准
        1. **知识点覆盖** ：题目需均匀分布在文本的各个关键章节，确保覆盖主要概念、事实、关系和重要细节
        2. **难度控制** ：选项应具有迷惑性，避免出现明显错误选项；正确答案不应过于明显或过于隐晦
        3. **题干要求** ：题干中需要避免出现“文中提到”、“根据文本”等类似字样。
        ### 选项设计规范
        1. 每个题目必须有且仅有4个选项(A/B/C/D)
        2. 选项长度应保持相近，避免通过长度差异暗示正确答案
        3. 错误选项应具有似真性，基于文本内容可能产生的误解设计
        4. 避免使用"以上都对"、"以上都不对"等非特异性选项
        5. 选项内容应相互独立，不包含重叠或包含关系
        6. 所有选项语法结构应保持一致，与问题形成合理搭配
        ### 答案准确性要求
        1. 正确答案必须100%来源于文本，确保绝对准确
        2. 答案位置(A/B/C/D)应随机分布，避免出现固定模式
        3. 每个题目只能有一个明确正确的答案
        ## 格式输出规范
        1. **唯一输出内容** ：仅返回一个标准JSON数组，不包含任何前置说明、后置解释、格式标记或注释
        2. **JSON结构** ：
        ```
        [
        {
            "question": "完整的问题描述，以问号结尾",
            "options": ["选项A内容", "选项B内容", "选项C内容", "选项D内容"],
            "answer": "A"  // 只能是单个大写字母(A/B/C/D)
        },
        // 更多题目...
        ]
        ```
        3. **格式约束** ：
        * 严格使用双引号，不使用单引号
        * 确保JSON语法完全正确，可直接解析
        * 问题和选项中不包含任何Markdown格式
        * 选项文本不包含序号(A./B.等)
        ## 示例
        ### 正确示例（仅为示例，非文本中内容）
        ```
        [
        {
            "question": "光合作用的主要产物是什么？",
            "options": ["氧气和葡萄糖", "二氧化碳和水", "氮气和氧气", "氢气和氧气"],
            "answer": "A"
        }
        ]
        ```
        ### 错误示例（请勿模仿）
        ```
        // 这是错误示例，包含了注释和多余文本
        [
        {
            "题目": "光合作用的主要产物？",  // 使用了错误的字段名
            "选项": ["氧气", "二氧化碳", "水"],  // 选项数量不足
            "正确答案": "氧气"  // 使用了错误的字段名和值格式
        }
        ]
        ```
        ## 执行流程
        1. 首先通读全文，识别并标记5-8个关键知识点区域
        2. 为每个区域设计相应数量的题目，确保覆盖全面
        3. 为每个题目设计4个选项，其中1个正确答案，3个具有迷惑性的错误选项
        4. 检查所有题目确保符合上述质量和格式要求
        5. 随机调整答案位置，确保分布均匀
        6. 仅输出最终JSON数组，不包含任何其他内容
        请根据以上要求，基于以下文本内容生成"""+f'{count}'+"道四选一选择题："+
        f'{merged_text}'
    )
    client = openai.OpenAI(
        api_key=api_config.get('api_key', ''),
        base_url=api_config.get('base_url', ''),
    )
    completion = client.chat.completions.create(
        model=api_config.get('model_name', 'qwen-max'),
        messages=[
            {"role": "system", "content": "你是一个专业的教育内容生成AI。"},
            {"role": "user", "content": prompt}
        ],
    )
    response_text = completion.choices[0].message.content
    response_text = filter_markdown(response_text)
    print(response_text)
    try:
        data = pyjson.loads(response_text)
        # 兼容AI返回外层包裹对象或直接数组
        if isinstance(data, dict):
            # 只取第一个值为题目数组
            for v in data.values():
                if isinstance(v, list):
                    data = v
                    break
        if not isinstance(data, list):
            raise ValueError('API返回内容不是题目数组')
    except Exception as e:
        raise ValueError(f'API返回内容无法解析为题目数组: {response_text}')
    print(data)
    results = []
    for item in data:
        question = item.get('question')
        options = item.get('options')
        answer = item.get('answer')
        if not question or not isinstance(options, list) or len(options) != 4 or answer not in ['A', 'B', 'C', 'D']:
            continue  # 跳过格式不正确的题目
        # 随机打乱选项并更新答案
        option_map = list(zip(['A', 'B', 'C', 'D'], options))
        random.shuffle(option_map)
        shuffled_options = [opt for _, opt in option_map]
        original_answer_content = options[ord(answer) - ord('A')]
        for idx, (_, opt) in enumerate(option_map):
            if opt == original_answer_content:
                new_answer = chr(ord('A') + idx)
                break
        else:
            new_answer = None
        results.append(("", question, shuffled_options, new_answer))
    return results

def generate_question_by_ollama_batch(text_list, count=1, model=OLLAMA_MODEL_NAME):
    """
    批量方式，根据text_list拼接为长文本，调用ollama生成题目。
    :param text_list: 文本列表，每个元素为一页内容
    :param count: 生成题目数量
    :param model: ollama模型名
    :return: [(prompt, question, options, answer), ...]
    """
    if not isinstance(text_list, list) or not text_list:
        raise ValueError('text_list必须为非空列表')
    # 拼接文本，每页加页码
    merged_text = "\n".join([
        f"【第{i+1}页开始】\n{text}\n【第{i+1}页结束】" for i, text in enumerate(text_list)
    ])
    prompt = (
        """
        # 高质量选择题生成专家提示词
        ## 角色定位
        你是一位拥有5年以上教育评估经验的试题生成专家，擅长从文本中提取关键信息并转化为有效评估题目。你的任务是基于提供的文本内容，生成高质量、诊断性强的四选一选择题，帮助全面评估读者对文本的理解程度。
        ## 任务描述
        请根据以下提供的文本内容，生成**"""+
        f'{count}'+
        """道**四选一选择题。所有题目必须直接来源于文本内容，不得加入任何外部知识。题目应能有效测试读者对文本关键信息的理解和应用能力，而非简单记忆。
        ## 内容质量要求
        ### 题目设计标准
        1. **知识点覆盖** ：题目需均匀分布在文本的各个关键章节，确保覆盖主要概念、事实、关系和重要细节
        2. **难度控制** ：选项应具有迷惑性，避免出现明显错误选项；正确答案不应过于明显或过于隐晦
        3. **题干要求** ：题干中需要避免出现“文中提到”、“根据文本”等类似字样。
        ### 选项设计规范
        1. 每个题目必须有且仅有4个选项(A/B/C/D)
        2. 选项长度应保持相近，避免通过长度差异暗示正确答案
        3. 错误选项应具有似真性，基于文本内容可能产生的误解设计
        4. 避免使用"以上都对"、"以上都不对"等非特异性选项
        5. 选项内容应相互独立，不包含重叠或包含关系
        6. 所有选项语法结构应保持一致，与问题形成合理搭配
        ### 答案准确性要求
        1. 正确答案必须100%来源于文本，确保绝对准确
        2. 答案位置(A/B/C/D)应随机分布，避免出现固定模式
        3. 每个题目只能有一个明确正确的答案
        ## 格式输出规范
        1. **唯一输出内容** ：仅返回一个标准JSON数组，不包含任何前置说明、后置解释、格式标记或注释
        2. **JSON结构** ：
        ```
        [
        {
            "question": "完整的问题描述，以问号结尾",
            "options": ["选项A内容", "选项B内容", "选项C内容", "选项D内容"],
            "answer": "A"  // 只能是单个大写字母(A/B/C/D)
        },
        // 更多题目...
        ]
        ```
        3. **格式约束** ：
        * 严格使用双引号，不使用单引号
        * 确保JSON语法完全正确，可直接解析
        * 问题和选项中不包含任何Markdown格式
        * 选项文本不包含序号(A./B.等)
        ## 示例
        ### 正确示例（仅为示例，非文本中内容）
        ```
        [
        {
            "question": "光合作用的主要产物是什么？",
            "options": ["氧气和葡萄糖", "二氧化碳和水", "氮气和氧气", "氢气和氧气"],
            "answer": "A"
        }
        ]
        ```
        ### 错误示例（请勿模仿）
        ```
        // 这是错误示例，包含了注释和多余文本
        [
        {
            "题目": "光合作用的主要产物？",  // 使用了错误的字段名
            "选项": ["氧气", "二氧化碳", "水"],  // 选项数量不足
            "正确答案": "氧气"  // 使用了错误的字段名和值格式
        }
        ]
        ```
        ## 执行流程
        1. 首先通读全文，识别并标记5-8个关键知识点区域
        2. 为每个区域设计相应数量的题目，确保覆盖全面
        3. 为每个题目设计4个选项，其中1个正确答案，3个具有迷惑性的错误选项
        4. 检查所有题目确保符合上述质量和格式要求
        5. 随机调整答案位置，确保分布均匀
        6. 仅输出最终JSON数组，不包含任何其他内容
        请根据以上要求，基于以下文本内容生成"""+f'{count}'+"道四选一选择题："+
        f'{merged_text}'
    )
    print("开始调用ollama批量出题")
    response = ollama.generate(
        model=model,
        prompt=prompt,
        stream=False,
        think=False
    )
    print("ollama批量出题完成")
    response_text = response.get('response', '')
    response_text = filter_markdown(response_text)
    try:
        data = pyjson.loads(response_text)
        # 兼容AI返回外层包裹对象或直接数组
        if isinstance(data, dict):
            for v in data.values():
                if isinstance(v, list):
                    data = v
                    break
        if not isinstance(data, list):
            raise ValueError('ollama返回内容不是题目数组')
    except Exception as e:
        raise ValueError(f'ollama返回内容无法解析为题目数组: {response_text}')
    print(data)
    results = []
    for item in data:
        question = item.get('question')
        options = item.get('options')
        answer = item.get('answer')
        if not question or not isinstance(options, list) or len(options) != 4 or answer not in ['A', 'B', 'C', 'D']:
            continue  # 跳过格式不正确的题目
        # 随机打乱选项并更新答案
        option_map = list(zip(['A', 'B', 'C', 'D'], options))
        random.shuffle(option_map)
        shuffled_options = [opt for _, opt in option_map]
        original_answer_content = options[ord(answer) - ord('A')]
        for idx, (_, opt) in enumerate(option_map):
            if opt == original_answer_content:
                new_answer = chr(ord('A') + idx)
                break
        else:
            new_answer = None
        results.append(("", question, shuffled_options, new_answer))
    return results
