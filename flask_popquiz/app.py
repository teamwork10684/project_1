from flask import Flask, request, jsonify
import ollama
from flask_cors import CORS
from module.aifilter.aifilter import filter_markdown

app = Flask(__name__)
CORS(app, supports_credentials=True)

OLLAMA_MODEL = 'deepseek-r1:7b'

@app.route('/popquiz/getQuestionByTextOllamaDemo', methods=['POST'])
def get_question_by_text_demo():
    data = request.get_json()
    original_prompt = data.get('original_prompt', '').strip()
    if not original_prompt:
        return jsonify({'message': '参数 original_prompt 不能为空'}), 400
    prompt = (
        "你是一名专业的教育内容生成AI，请根据用户提供的原始文本内容，生成一道单项选择题。"
        "请严格按照以下要求输出：\n"
        "1. 题目内容应与原始文本高度相关，简明扼要，问题长度尽可能地短。\n"
        "2. 只生成一道题目。\n"
        "3. 只输出JSON格式，包含三个字段：question（字符串，题目内容），options（字符串数组，长度为4，4个选项）,answer(A、B、C、D中的一个，只需要给出对应选项字母，不用重复选项内容!!!)。\n"
        "4. 选项内容应合理且互不重复，只有一个正确答案，其余为干扰项。\n"
        "5. 不要输出除JSON以外的任何内容。\n"
        "6. JSON示例{\"question\":\"问题\",\"options\":[\"选项A\",\"选项B\",\"选项C\",\"选项D\"],\"answer\":\"A\"}\n"
        f"原始文本：{original_prompt}"
        "注意！除了返回json格式的回答外不要返回任何其他内容！！！"
    )
    try:
        print(original_prompt)
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            stream=False,
            think=False
        )
        import json as pyjson
        response_text = response.get('response', '')
        response_text = filter_markdown(response_text)
        print(response_text)
        try:
            data = pyjson.loads(response_text)
            question = data.get('question')
            options = data.get('options')
            answer = data.get('answer')
            if not question or not isinstance(options, list) or len(options) != 4 or answer not in ['A', 'B', 'C', 'D']:
                raise ValueError('AI返回格式不正确')
            # 随机打乱选项并更新答案
            import random
            option_map = list(zip(['A', 'B', 'C', 'D'], options))
            random.shuffle(option_map)
            shuffled_options = [opt for _, opt in option_map]
            # 找到原答案对应的内容
            original_answer_content = options[ord(answer) - ord('A')]
            # 新的answer字母
            for idx, (_, opt) in enumerate(option_map):
                if opt == original_answer_content:
                    new_answer = chr(ord('A') + idx)
                    break
            else:
                new_answer = None
            return jsonify({'question': question, 'options': shuffled_options, 'answer': new_answer})
        except Exception:
            return jsonify({'message': 'AI返回内容解析失败', 'raw': response_text}), 400
    except Exception as e:
        return jsonify({'message': f'AI服务异常: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
