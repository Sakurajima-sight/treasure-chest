import re
from dotenv import load_dotenv
from openai import OpenAI
import os
import time
import json

# 加载环境变量
load_dotenv()
QWEN3_API_KEY = os.getenv("QWEN3_API_KEY")
GPT_API_KEY = os.getenv("GPT_API_KEY")
DEFAULT_MODEL = "qwen-max"

markdown2bilingual_prompt = """**翻译规则说明：**

1. **标题对照**：所有英文标题和子标题，英文标题的后面紧跟翻译的中文标题，或者英文子标题的后面紧跟翻译的中文的子标题，同处一行，你不要只保留了中文标题或是中文子标题，而漏掉了英文标题或者英文的子标题。英文标题和中文标题之间仅用空格分隔，不添加其他符号，不用添加任"#"，同时英文标题要保留原先在markdown中原有的样式。
2. **对照格式**：每个英文句子后面跟着对应的中文翻译，但英语句子和对应的中文翻译两者间需换行。每对英文句子与中文翻译之间需空一行。
3. **只翻译所给内容**：仅翻译我所提供的文本内容，不凭空添加或遗漏信息，不要添加任何内容。如果我发给你的内容中遇到“__Image_Placeholder_{image_counter}__”直接保留，仅仅需要保留唯一一个标识符，标识符要唯一，不需要翻译。
"""

def clean_and_extract_markdown(text):
    # 移除 <think>...</think> 内容
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()

    # 提取 markdown 代码块（```markdown ... ``` 或 ``` ... ```)
    codeblock_pattern = r"```(?:markdown)?\s*([\s\S]+?)\s*```"
    match = re.search(codeblock_pattern, text)
    if match:
        content = match.group(1).strip()
    else:
        content = text.strip()

    # 去除重复标签，例如多个 __Image_Placeholder_1__ 保留一个
    content = re.sub(r'(\b_+Image_Placeholder_\d+_+\b)(?:\s*\1)+', r'\1', content)

    return content

# 定义与模型交互的函数
def ask_model(prompt_text, model=DEFAULT_MODEL, max_retries=3, retry_interval=2):
    client = OpenAI(
        api_key=QWEN3_API_KEY,
        base_url="https://ai.erikpsw.works",
    )
    for attempt in range(1, max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt_text}],
                temperature=0.0,
                stream=True
            )
            full_reply_content = ""
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta.content:
                    full_reply_content += chunk.choices[0].delta.content
            return full_reply_content.strip()
        except Exception as e:
            pass
        if attempt < max_retries:
            time.sleep(retry_interval)
    raise Exception(f"接口请求失败，已重试{max_retries}次仍未成功。")


def ask_gpt(prompt_text, api_key=GPT_API_KEY, base_url="https://api.pumpkinaigc.online/v1", model="gpt-4.1-nano"):
    """
    向 GPT 模型发送请求并返回模型回答。

    参数:
    - prompt_text (str): 用户输入的文本
    - api_key (str): OpenAI API 密钥
    - base_url (str): OpenAI API 的基础 URL
    - model (str): 要使用的模型，默认使用 "gpt-4.1-nano"

    返回:
    - str: GPT 模型的回答
    """
    try:
        # 创建 OpenAI 客户端
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        # 向 GPT 发送请求并获取响应
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt_text}
            ],
            model=model
        )

        # 返回模型生成的内容
        return chat_completion.choices[0].message.content

    except Exception as e:
        # 如果请求失败，返回错误信息
        return f"请求失败: {str(e)}"

# 定义转换 Markdown 内容为列表的函数
def convert_markdown_to_list(file_path):
    # 存储最终的列表
    result = []
    
    # 正则表达式用于匹配图片标签和标题
    img_pattern = r'<p align="center"><img [^>]*src="([^"]+)"[^>]*alt="([^"]*)"[^>]*></p>'
    header_pattern = r'(#{1,6})\s*(.*)'  # 匹配标题，# 表示层级
    
    # 用于替换图片占位符
    image_counter = 0
    img_placeholders = {}  # 存储占位符与图片的对应关系
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as file:
        md_content = file.read()

    # 替换图片标签为占位符并生成标题、子标题及其内容
    lines = md_content.splitlines()
    current_content = ""
    
    for line in lines:
        # 处理图片标签 (支持普通图片和base64嵌入图片)
        img_match = re.match(img_pattern, line)

        if img_match:
            # 替换图片标签为占位符
            image_counter += 1
            img_placeholder = f"__Image_Placeholder_{image_counter}__"
            img_placeholders[img_placeholder] = img_match.group(0)
            current_content += img_placeholder + "\n"
            continue
        
        # 处理标题
        header_match = re.match(header_pattern, line)
        if header_match:
            if current_content.strip():  # 如果当前内容非空，先将之前的内容加入结果
                result.append(current_content.strip())
            # 添加标题
            current_content = header_match.group(0).strip() + "\n"
            continue
        
        # 如果是普通内容，加入到当前内容中
        if line.strip():
            current_content += line.strip() + "\n"
    
    # 最后加入最后的内容
    if current_content.strip():
        result.append(current_content.strip())

    return result, img_placeholders

# 定义转换为双语 Markdown 并保存到文件的函数
def convert_to_bilingual_md(input_file_path, output_file_path):
    result, img_placeholders = convert_markdown_to_list(input_file_path)

    bilingual_content_list = [img_placeholders[result[0]]]

    # 循环处理每个内容块并翻译成双语
    for idx, item in enumerate(result[1:], 1):
        prompt = f'"{item}"{markdown2bilingual_prompt}'
        bilingual_content = ask_gpt(prompt)
        bilingual_content = clean_and_extract_markdown(bilingual_content)
        print(bilingual_content)
        # 倒序遍历占位符，恢复图片占位符为原始图片标签
        for placeholder, img_tag in reversed(img_placeholders.items()):
            bilingual_content = bilingual_content.replace(placeholder, img_tag)
        bilingual_content_list.append(bilingual_content)
        time.sleep(2)

    # 将双语内容写入到输出文件
    with open(output_file_path, 'w', encoding='utf-8') as f:
        for item in bilingual_content_list:
            f.write(item + "\n")

# 执行脚本，将原始文件转换为双语文件
file_path = '1.AC Waveform and AC Circuit Theory split sentence.md'
output_file_path = '1.AC Waveform and AC Circuit Theory bilingual.md'
convert_to_bilingual_md(file_path, output_file_path)
