import requests
import re
import os
import time
import argparse
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("QWEN3_API_KEY")
API_URL = "https://ai.erikpsw.works/v1/chat/completions"
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3-235b-a22b-non-thinking")

def clean_and_extract_markdown(text):
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    codeblock_pattern = r"```(?:markdown)?\s*([\s\S]+?)\s*```"
    match = re.search(codeblock_pattern, text)
    if match:
        return match.group(1).strip()
    else:
        return text.strip()

def ask_model(prompt_text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt_text}
        ]
    }
    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
    else:
        return f"请求失败，状态码: {response.status_code}, 内容: {response.text}"

def process_html_to_markdown(html_path, output_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = r'第\s*\d+\s*组内容\s*([\s\S]*?)(?=第\s*\d+\s*组内容|$)'
    groups = re.findall(pattern, content)
    if os.path.exists(output_path):
        os.remove(output_path)
    for idx, group_content in enumerate(groups, 1):
        prompt = group_content.strip()
        if not prompt:
            continue
        try:
            reply = ask_model(prompt)
            time.sleep(2)
        except Exception as e:
            print(f"第{idx}组出错：{e}")
            continue
        reply_clean = clean_and_extract_markdown(reply)
        with open(output_path, 'a', encoding='utf-8') as md:
            md.write(reply_clean + "\n\n")
        print(f"第{idx}组内容已处理并写入Markdown。")
        print(reply_clean)
    print("全部处理完成！")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量处理Markdown文件的内容翻译")
    parser.add_argument('-i', '--input', type=str, required=True, help='输入Markdown文件路径')
    parser.add_argument('-o', '--output', type=str, required=True, help='输出Markdown文件路径')
    args = parser.parse_args()

    process_html_to_markdown(
        html_path=args.input,
        output_path=args.output
    )
