import ollama
from module.aifilter.aifilter import filter_markdown
import json as pyjson
import random
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
        "你是一名专业的教育内容生成AI，请根据用户提供的原始文本内容，生成一道高质量的单项选择题。"
        "请严格遵循以下要求，仅输出JSON格式的结果：\n"
        "1. 题目内容必须与原文高度相关，避免常识题或与原文无关的泛泛问题。\n"
        "2. 题干应简洁明了，避免冗长和歧义，突出考查原文核心信息。\n"
        "3. 只生成一道题目。\n"
        "4. 选项必须4个，内容互不重复、无歧义，且只有一个正确答案，其余为合理干扰项。\n"
        "5. 干扰项应与正确答案有一定迷惑性，但不能与原文事实冲突。\n"
        "6. 答案必须唯一且明确，不能有多解。\n"
        "7. 题目难度适中，既不能太简单（如直接照抄原文），也不能太难（如超纲推理）。\n"
        "8. 只输出严格的JSON格式，包含如下字段：\n"
        "   question（字符串，题目内容），options（字符串数组，长度为4，4个选项），answer（A、B、C、D中的一个，只需字母）。\n"
        "9. 不要输出除JSON以外的任何内容，不要有解释、说明、markdown、代码块、标签等。\n"
        "10. JSON示例：{\"question\":\"问题\",\"options\":[\"选项A\",\"选项B\",\"选项C\",\"选项D\"],\"answer\":\"A\"}\n"
        f"原始文本：{text}\n"
        "（注意！除了返回json格式的回答外不要返回任何其他内容！不要有多余的换行、空格、注释、代码块、解释等！）"
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
    print(data)
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
        "你是一名专业的教育内容生成AI，请根据用户提供的原始文本内容，生成一道高质量的单项选择题。"
        "请严格遵循以下要求，仅输出JSON格式的结果：\n"
        "1. 题目内容必须与原文高度相关，避免常识题或与原文无关的泛泛问题。\n"
        "2. 题干应简洁明了，避免冗长和歧义，突出考查原文核心信息。\n"
        "3. 只生成一道题目。\n"
        "4. 选项必须4个，内容互不重复、无歧义，且只有一个正确答案，其余为合理干扰项。\n"
        "5. 干扰项应与正确答案有一定迷惑性，但不能与原文事实冲突。\n"
        "6. 答案必须唯一且明确，不能有多解。\n"
        "7. 题目难度适中，既不能太简单（如直接照抄原文），也不能太难（如超纲推理）。\n"
        "8. 只输出严格的JSON格式，包含如下字段：\n"
        "   question（字符串，题目内容），options（字符串数组，长度为4，4个选项），answer（A、B、C、D中的一个，只需字母）。\n"
        "9. 不要输出除JSON以外的任何内容，不要有解释、说明、markdown、代码块、标签等。\n"
        "10. JSON示例：{\"question\":\"问题\",\"options\":[\"选项A\",\"选项B\",\"选项C\",\"选项D\"],\"answer\":\"A\"}\n"
        f"原始文本：{text}\n"
        "（注意！除了返回json格式的回答外不要返回任何其他内容！不要有多余的换行、空格、注释、代码块、解释等！）"
    )
    client = openai.OpenAI(
        api_key=api_config.get('api_key', ''),
        base_url=api_config.get('base_url', ''),
    )
    completion=client.chat.completions.create(
        model=api_config.get('model_name', 'qwen-max'),
        messages=[
            {"role": "system", "content": "你是一个专业的教育内容生成AI。"},
            {"role": "user", "content": prompt}
        ],
    )
    print(completion.model_dump_json())
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

def generate_question(text, is_batch=False):
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
        return generate_question_by_api(text, API_CONFIG)
    else:
        if not OLLAMA_MODEL_NAME:
            raise ValueError('ollama模型名不能为空')
        return generate_question_by_ollama(text, OLLAMA_MODEL_NAME)

def generate_question_by_api_batch(text_list):
    """通过API批量生成题目，返回题目结果列表"""
    results = []
    for text in text_list:
        try:
            res = generate_question(text, is_batch=True)
            results.append(res)
        except Exception as e:
            print(f"API批量出题失败: {e}")
    return results

def generate_question_by_ollama_batch(text_list):
    """通过Ollama批量生成题目，返回题目结果列表"""
    results = []
    for text in text_list:
        try:
            # 这里假设有ollama专用的生成逻辑
            res = generate_question(text, is_batch=True)
            results.append(res)
        except Exception as e:
            print(f"Ollama批量出题失败: {e}")
    return results 
