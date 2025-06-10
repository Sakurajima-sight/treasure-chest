import streamlit as st
import requests
import os
from dotenv import load_dotenv
from st_chat_message import message

# 加载环境变量
load_dotenv()

# API Key 和模型设置
API_KEY = os.getenv("QWEN3_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "qwen3-235b-a22b-non-thinking")
API_URL = "https://ai.erikpsw.works/v1/chat/completions"

# 发送请求的函数
def ask_model(prompt_text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    # 请求数据体
    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt_text}
        ]
    }
    
    # 发送 POST 请求
    response = requests.post(API_URL, headers=headers, json=data)
    
    if response.status_code == 200:
        try:
            result = response.json()
            # 检查返回内容是否有预期的字段
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
            else:
                return "没有收到有效的响应，请稍后再试。"
        except Exception as e:
            return f"解析响应失败: {str(e)}"
    else:
        return f"请求失败，状态码: {response.status_code}, 内容: {response.text}"

# Streamlit 界面
st.title("Chatbot using Qwen3 Model")
st.write("欢迎与机器人对话！")

# 用户输入，多行输入框
user_input = st.text_area("你:", "", height=150)

# 发送按钮
if st.button("发送"):
    if user_input:
        # 获取 API 响应
        bot_response = ask_model(user_input)
        
        # 显示消息
        message(user_input, is_user=True)
        message(bot_response)
    else:
        st.warning("请输入消息后点击发送。")
