import re

def filter_markdown(response_text: str) -> str:
    """
    检查 response_text 是否为 ```json ... ``` 格式，如果是则提取内容，否则原样返回。
    """
    pattern = r"```json\s*([\s\S]*?)\s*```"
    match = re.search(pattern, response_text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return response_text
