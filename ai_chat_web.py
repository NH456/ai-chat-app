import json
import os
from openai import OpenAI
import streamlit as st

# ---------- 火山引擎配置（按你的情况修改） ----------
API_KEY = "ark-83732f77-dbe9-4fd7-b9c4-a51691409da3-4ceab"  # 你的火山API Key
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"  # 火山固定地址
MODEL = "ep-20260530002352-rq9br"  # 你的DeepSeek接入点ID
HISTORY_FILE = "chat_history.json"

# ---------- 初始化客户端 ----------
client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

# ---------- 页面标题 ----------
st.set_page_config(page_title="火山AI聊天助手", page_icon="💬")
st.title("💬 AI聊天助手")
st.caption("支持对话记忆，刷新页面或重启后历史仍在")

# ---------- 初始化session_state（存储当前会话消息） ----------
if "messages" not in st.session_state:
    # 尝试从文件加载历史
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            st.session_state.messages = json.load(f)
        st.info(f"加载了 {len(st.session_state.messages)//2} 轮历史记录")
    else:
        st.session_state.messages = []

# ---------- 显示历史消息 ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- 接收用户输入 ----------
if prompt := st.chat_input("说点什么..."):
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 调用AI并显示回复
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model=MODEL,
            messages=st.session_state.messages
        )
        reply = response.choices[0].message.content
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    
    # 实时保存到文件（每次对话后保存）
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False)

# ---------- 侧边栏按钮 ----------
with st.sidebar:
    st.header("控制面板")
    if st.button("🗑️ 清空历史"):
        st.session_state.messages = []
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.rerun()
    if st.button("💾 手动保存"):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False)
        st.success("已保存")