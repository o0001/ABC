import streamlit as st
import openai
import base64
from datetime import datetime
import pandas as pd

# ---------- 页面配置 ----------
st.set_page_config(page_title="数学学习助手", layout="wide")

# ---------- 初始化 session_state ----------
if "notes" not in st.session_state:
    st.session_state.notes = []  # 每条笔记: {"text":..., "tags":[...], "time":...}
if "messages" not in st.session_state:
    st.session_state.messages = []  # 聊天记录
if "ai_prompt" not in st.session_state:
    st.session_state.ai_prompt = ""  # 从 pg2 传来的预设问题
if "wiki_links" not in st.session_state:
    # 预留给你的维基百科数学概念链接，你可以自行修改和添加
    st.session_state.wiki_links = [
        {"title": "代数", "url": "https://en.wikipedia.org/wiki/Algebra"},
        {"title": "几何", "url": "https://en.wikipedia.org/wiki/Geometry"},
        {"title": "微积分", "url": "https://en.wikipedia.org/wiki/Calculus"},
        {"title": "线性代数", "url": "https://en.wikipedia.org/wiki/Linear_algebra"},
        {"title": "概率论", "url": "https://en.wikipedia.org/wiki/Probability_theory"},
    ]
if "basic_tags" not in st.session_state:
    st.session_state.basic_tags = ["代数", "几何", "微积分", "线性代数", "概率", "数论", "拓扑", "组合数学", "数学分析"]

# ---------- 侧边栏：全局设置与导航 ----------
st.sidebar.title("📐 数学学习助手")
page = st.sidebar.radio("导航", ["📝 笔记与标签", "🔗 维基百科链接", "🤖 AI 对话"])

# OpenAI API Key
api_key = st.sidebar.text_input("输入 OpenAI API Key", type="password")
if api_key:
    openai.api_key = api_key

# ---------- 工具函数 ----------
def image_to_base64(image_file):
    """将上传的图片转为 base64 字符串"""
    return base64.b64encode(image_file.read()).decode("utf-8")

# ---------- 页面1: 笔记与标签 ----------
if page == "📝 笔记与标签":
    st.header("📝 数学笔记")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        note_text = st.text_area("写点数学笔记...", height=200)
        selected_basic_tags = st.multiselect("选择基本标签", st.session_state.basic_tags)
        custom_tags_input = st.text_input("自定义标签（用逗号分隔）", placeholder="例如: 公式, 定理, 错题")
        
        if st.button("保存笔记"):
            if note_text.strip():
                # 处理自定义标签
                custom_tags = [t.strip() for t in custom_tags_input.split(",") if t.strip()]
                all_tags = selected_basic_tags + custom_tags
                st.session_state.notes.append({
                    "text": note_text,
                    "tags": all_tags,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                st.success("笔记已保存！")
            else:
                st.warning("笔记内容不能为空")
    
    with col2:
        st.subheader("所有笔记")
        if not st.session_state.notes:
            st.info("还没有笔记，快写一条吧")
        else:
            for i, note in enumerate(reversed(st.session_state.notes)):
                with st.expander(f"笔记 {len(st.session_state.notes)-i} - {note['time']}"):
                    st.markdown(note["text"])
                    if note["tags"]:
                        st.caption("标签: " + ", ".join(note["tags"]))
                    if st.button("删除", key=f"del_{i}"):
                        del st.session_state.notes[len(st.session_state.notes)-1-i]
                        st.rerun()

# ---------- 页面2: 维基百科链接 ----------
elif page == "🔗 维基百科链接":
    st.header("🔗 数学概念 · 维基百科")
    st.caption("点击按钮可将概念发送到 AI 对话页进行问答")
    
    for i, link in enumerate(st.session_state.wiki_links):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown(f"**{link['title']}**")
        with col2:
            st.markdown(f"[{link['url']}]({link['url']})")
        with col3:
            if st.button("问 AI", key=f"ask_{i}"):
                st.session_state.ai_prompt = f"请解释这个数学概念：{link['title']}，参考链接：{link['url']}"
                st.success("已复制到 AI 对话，切换页面即可查看")
    
    st.divider()
    st.subheader("➕ 添加你自己的维基链接")
    new_title = st.text_input("概念名称", placeholder="例如：傅里叶变换")
    new_url = st.text_input("维基百科 URL", placeholder="https://en.wikipedia.org/wiki/...")
    if st.button("添加链接"):
        if new_title and new_url:
            st.session_state.wiki_links.append({"title": new_title, "url": new_url})
            st.success("链接已添加")
            st.rerun()
        else:
            st.warning("请填写完整信息")

# ---------- 页面3: AI 对话与图片上传 ----------
elif page == "🤖 AI 对话":
    st.header("🤖 AI 数学助教")
    
    if not api_key:
        st.warning("请先在侧边栏输入 OpenAI API Key")
    else:
        # 如果有从 pg2 传来的预设问题，自动填入输入框
        prompt_from_pg2 = st.session_state.ai_prompt
        if prompt_from_pg2:
            st.info(f"📋 来自维基页面的问题：{prompt_from_pg2}")
            # 清空传递变量，避免重复显示
            st.session_state.ai_prompt = ""
        
        # 聊天历史显示
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # 输入区域
        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_area("输入你的数学问题", value=prompt_from_pg2, height=100, placeholder="例如：解释一下黎曼猜想...")
            uploaded_image = st.file_uploader("上传图片（可选，支持数学公式、题目截图）", type=["png", "jpg", "jpeg"])
            submit_button = st.form_submit_button("发送")
        
        if submit_button and (user_input.strip() or uploaded_image):
            # 准备用户消息
            if uploaded_image:
                base64_image = image_to_base64(uploaded_image)
                image_url = f"data:image/jpeg;base64,{base64_image}"
                # 构建用户消息，包含图片和文字
                user_message_content = [
                    {"type": "text", "text": user_input if user_input.strip() else "请分析这张图片中的数学内容"},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            else:
                user_message_content = user_input.strip()
            
            # 添加到历史
            st.session_state.messages.append({"role": "user", "content": user_message_content})
            
            # 调用 OpenAI API
            with st.spinner("思考中..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4o",  # 支持视觉的模型
                        messages=st.session_state.messages,
                        max_tokens=1000
                    )
                    assistant_reply = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
                    st.rerun()
                except Exception as e:
                    st.error(f"出错了：{e}")
        
        # 清空对话按钮
        if st.button("清空对话历史"):
            st.session_state.messages = []
            st.rerun()
