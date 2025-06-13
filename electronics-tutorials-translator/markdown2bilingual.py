import requests
import re
import os
import time
import argparse
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

API_KEY = os.getenv("QWEN3_API_KEY")
API_URL = "https://ai.erikpsw.works/v1/chat/completions"
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3-235b-a22b")

def clean_and_extract_markdown(text):
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    codeblock_pattern = r"```(?:markdown)?\s*([\s\S]+?)\s*```"
    match = re.search(codeblock_pattern, text)
    if match:
        return match.group(1).strip()
    else:
        return text.strip()

def ask_model(prompt_text, max_retries=3, retry_interval=2):
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://ai.erikpsw.works",
    )
    for attempt in range(1, max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model="qwen3-235b-a22b",
                messages=[
                    {"role": "user", "content": prompt_text},
                ],
                temperature=0.0,
                stream=True  # 开启流式
            )
            full_reply_content = ""
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta.content:
                    full_reply_content += chunk.choices[0].delta.content
            return full_reply_content
        except Exception as e:
            print(f"请求异常：{e}（第{attempt}次尝试）")
        if attempt < max_retries:
            time.sleep(retry_interval)
    # 超过最大重试次数仍失败，抛出异常
    raise Exception(f"接口请求失败，已重试{max_retries}次仍未成功。")

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
