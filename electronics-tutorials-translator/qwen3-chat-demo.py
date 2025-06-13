import streamlit as st
import requests
import os
from dotenv import load_dotenv
from st_chat_message import message
from openai import OpenAI
import time
import re

# 加载环境变量
load_dotenv()

API_KEY = os.getenv("QWEN3_API_KEY")
DEFAULT_MODEL = os.getenv("MODEL_NAME", "qwen3-235b-a22b-non-thinking")

MODEL_OPTIONS = {
    "Qwen3 235B Non-Thinking": "qwen3-235b-a22b-non-thinking",
    "Qwen3 235B": "qwen3-235b-a22b",
    "Qwen-Max": "qwen-max",
    "DeepSeek V3": "deepseek-v3",
    "DeepSeek R1": "deepseek-r1",
}

def clean_and_extract_markdown(text):
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    codeblock_pattern = r"```(?:markdown)?\s*([\s\S]+?)\s*```"
    match = re.search(codeblock_pattern, text)
    if match:
        return match.group(1).strip()
    else:
        return text.strip()

def ask_model(prompt_text, model, max_retries=3, retry_interval=2):
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://ai.erikpsw.works",
    )
    for attempt in range(1, max_retries + 1):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": prompt_text},
                ],
                temperature=0.0,
                stream=True  # 流式输出
            )
            full_reply_content = ""
            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta.content:
                    full_reply_content += chunk.choices[0].delta.content
            print(full_reply_content)
            return full_reply_content
        except Exception as e:
            print(f"请求异常：{e}（第{attempt}次尝试）")
        if attempt < max_retries:
            time.sleep(retry_interval)
    raise Exception(f"接口请求失败，已重试{max_retries}次仍未成功。")

# Streamlit 界面
st.title("Chatbot using Multiple LLMs")
st.write("欢迎与机器人对话！")

# 新增：模型选择下拉框
selected_model_display = st.selectbox(
    "选择模型",
    list(MODEL_OPTIONS.keys()),
    index=list(MODEL_OPTIONS.values()).index(DEFAULT_MODEL) if DEFAULT_MODEL in MODEL_OPTIONS.values() else 0
)
selected_model = MODEL_OPTIONS[selected_model_display]

user_input = st.text_area("你:", "", height=150)

if st.button("发送"):
    if user_input:
        bot_response = ask_model(user_input, selected_model)
        message(user_input, is_user=True)
        message(bot_response)
    else:
        st.warning("请输入消息后点击发送。")
