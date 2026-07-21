import streamlit as st
import openai
import base64
import os
from datetime import datetime
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
from abc import ABC, abstractmethod

# ---------- 기본 페이지 클래스 ----------
class PageBase(ABC):
    def __init__(self, title, icon):
        self.title = title
        self.icon = icon
    @abstractmethod
    def run(self):
        pass

# ---------- 세션 초기화 ----------
def init_session():
    defaults = {
        "notes": [],
        "messages": [],
        "ai_prompt": "",
        "wiki_links": [
            {"title": "대수학", "url": "https://en.wikipedia.org/wiki/Algebra"},
            {"title": "기하학", "url": "https://en.wikipedia.org/wiki/Geometry"},
            {"title": "미적분학", "url": "https://en.wikipedia.org/wiki/Calculus"},
            {"title": "선형대수학", "url": "https://en.wikipedia.org/wiki/Linear_algebra"},
            {"title": "확률론", "url": "https://en.wikipedia.org/wiki/Probability_theory"},
        ],
        "basic_tags": ["대수학", "기하학", "미적분학", "선형대수학", "확률", "정수론", "위상수학", "조합론", "수리해석"]
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def img_to_base64(f):
    return base64.b64encode(f.read()).decode("utf-8")

# ---------- 페이지 1: 노트 + 계산기 + 그래프 (통합, 간결) ----------
class NotesAndToolsPage(PageBase):
    def __init__(self):
        super().__init__("📝 노트 & 도구", "📝")
    
    def run(self):
        st.header(f"{self.icon} {self.title}")
        
        # ---- 노트 입력 (간단) ----
        with st.container(border=True):
            st.subheader("✍️ 새 노트")
            col1, col2 = st.columns([3, 1])
            with col1:
                text = st.text_area("내용 (Markdown + LaTeX 지원)", height=120, 
                                    placeholder="예: $\\sum_{k=1}^n k = n(n+1)/2$")
            with col2:
                img = st.file_uploader("이미지", type=["png","jpg","jpeg"], label_visibility="collapsed")
                if img:
                    st.image(img, width=120)
            tags = st.multiselect("태그", st.session_state.basic_tags, default=[], placeholder="선택 또는 입력")
            custom_tags = st.text_input("사용자 태그 (쉼표 구분)", placeholder="공식, 정리")
            if st.button("💾 저장", use_container_width=True):
                if text.strip() or img:
                    b64 = img_to_base64(img) if img else None
                    all_tags = tags + [t.strip() for t in custom_tags.split(",") if t.strip()]
                    st.session_state.notes.append({
                        "text": text,
                        "image": b64,
                        "tags": all_tags,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    st.success("저장 완료")
                    st.rerun()
                else:
                    st.warning("내용이나 이미지를 입력하세요")
        
        # ---- 노트 목록 (카드 형태) ----
        st.subheader("📚 기록")
        if not st.session_state.notes:
            st.info("아직 노트가 없어요")
        else:
            for idx, note in enumerate(reversed(st.session_state.notes)):
                with st.expander(f"📌 {note['time']}  {', '.join(note['tags'])}"):
                    st.markdown(note["text"])
                    if note.get("image"):
                        st.image(base64.b64decode(note["image"]), width=250)
                    if st.button("🗑 삭제", key=f"del_{idx}"):
                        del st.session_state.notes[len(st.session_state.notes)-1-idx]
                        st.rerun()
        
        st.divider()
        
        # ---- 계산기 & 그래프 (가로로 배치) ----
        col_calc, col_plot = st.columns(2)
        with col_calc:
            st.subheader("🧮 계산기")
            with st.container(border=True):
                calc_type = st.selectbox("유형", ["간소화", "미분", "적분", "방정식"], key="calc_type")
                expr = st.text_input("f(x) =", value="x**2 + 2*x + 1", key="expr")
                if st.button("계산", use_container_width=True):
                    try:
                        x = sp.symbols('x')
                        e = sp.sympify(expr)
                        if calc_type == "간소화":
                            res = sp.simplify(e)
                        elif calc_type == "미분":
                            res = sp.diff(e, x)
                        elif calc_type == "적분":
                            res = sp.integrate(e, x)
                        else:
                            if "=" in expr:
                                l,r = expr.split("=")
                                eq = sp.Eq(sp.sympify(l.strip()), sp.sympify(r.strip()))
                            else:
                                eq = sp.Eq(e, 0)
                            res = sp.solve(eq, x)
                        st.latex(sp.latex(res))
                    except Exception as e:
                        st.error(f"오류: {e}")
        
        with col_plot:
            st.subheader("📈 그래프")
            with st.container(border=True):
                func = st.text_input("f(x) =", value="sin(x)", key="plot_func")
                xmin = st.number_input("x 최소", value=-5.0, key="xmin")
                xmax = st.number_input("x 최대", value=5.0, key="xmax")
                if st.button("그리기", use_container_width=True):
                    try:
                        x_sym = sp.symbols('x')
                        f = sp.lambdify(x_sym, sp.sympify(func), "numpy")
                        xs = np.linspace(xmin, xmax, 400)
                        ys = f(xs)
                        fig, ax = plt.subplots(figsize=(5,3))
                        ax.plot(xs, ys, color="#2b8cbe")
                        ax.grid(True, linestyle="--", alpha=0.5)
                        ax.set_xlabel("x"); ax.set_ylabel("f(x)")
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"오류: {e}")

# ---------- 페이지 2: 위키 링크 (간소화) ----------
class WikiPage(PageBase):
    def __init__(self):
        super().__init__("🔗 위키백과", "🔗")
    
    def run(self):
        st.header(f"{self.icon} 수학 개념 위키")
        st.caption("개념을 선택하면 AI에게 질문할 수 있어요")
        
        for i, link in enumerate(st.session_state.wiki_links):
            cols = st.columns([3, 2, 1])
            with cols[0]:
                st.markdown(f"**{link['title']}**")
            with cols[1]:
                st.markdown(f"[바로가기]({link['url']})")
            with cols[2]:
                if st.button("🤖 질문", key=f"wiki_{i}"):
                    st.session_state.ai_prompt = f"다음 개념을 설명해줘: {link['title']} (참고: {link['url']})"
                    st.toast("AI 대화로 전송됨")
        
        st.divider()
        st.subheader("➕ 링크 추가")
        with st.container(border=True):
            c1,c2 = st.columns(2)
            with c1:
                title = st.text_input("이름", placeholder="푸리에 변환")
            with c2:
                url = st.text_input("URL", placeholder="https://...")
            if st.button("추가", use_container_width=True):
                if title and url:
                    st.session_state.wiki_links.append({"title": title, "url": url})
                    st.success("추가됨")
                    st.rerun()
                else:
                    st.warning("모두 입력하세요")

# ---------- 페이지 3: AI 대화 (깔끔한 채팅) ----------
class AIChatPage(PageBase):
    def __init__(self):
        super().__init__("🤖 AI 조교", "🤖")
    
    def run(self):
        st.header(f"{self.icon} AI 수학 조교")
        if not openai.api_key:
            st.warning("OpenAI API Key를 사이드바에 입력하세요")
            return
        
        prompt = st.session_state.pop("ai_prompt", "")
        if prompt:
            st.info(f"📩 {prompt}")
        
        # 채팅 기록 표시
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if isinstance(msg["content"], list):
                    for part in msg["content"]:
                        if part["type"] == "text":
                            st.markdown(part["text"])
                        elif part["type"] == "image_url":
                            st.image(part["image_url"]["url"], width=200)
                else:
                    st.markdown(msg["content"])
        
        # 입력
        with st.container():
            col1, col2 = st.columns([5,1])
            with col1:
                user_text = st.text_area("질문", value=prompt, height=80, 
                                         placeholder="수학 질문을 입력하세요", key="chat_input")
            with col2:
                uploaded = st.file_uploader("📎", type=["png","jpg","jpeg"], label_visibility="collapsed")
            if st.button("전송", use_container_width=True):
                if user_text.strip() or uploaded:
                    if uploaded:
                        b64 = img_to_base64(uploaded)
                        content = [
                            {"type": "text", "text": user_text if user_text.strip() else "이미지 분석해줘"},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                        ]
                    else:
                        content = user_text.strip()
                    st.session_state.messages.append({"role": "user", "content": content})
                    with st.spinner("생각 중..."):
                        try:
                            resp = openai.ChatCompletion.create(
                                model="gpt-4o",
                                messages=st.session_state.messages,
                                max_tokens=1024,
                                temperature=0.7
                            )
                            reply = resp.choices[0].message.content
                            st.session_state.messages.append({"role": "assistant", "content": reply})
                            st.rerun()
                        except Exception as e:
                            st.error(f"오류: {e}")
                else:
                    st.warning("질문을 입력하세요")
        
        if st.button("🗑 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# ---------- 메인 ----------
def main():
    st.set_page_config(page_title="수학 도우미", page_icon="📐", layout="wide")
    # 간결한 CSS
    st.markdown("""
    <style>
        .stApp { background: #fafafa; }
        .stButton>button { border-radius: 8px; font-weight: 500; }
        .stTextArea textarea { border-radius: 8px; }
        .stSelectbox, .stTextInput { border-radius: 8px; }
        .stExpander { border: 1px solid #e0e0e0; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)
    
    init_session()
    
    # 사이드바
    st.sidebar.title("📐 수학 도우미")
    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        value=os.environ.get("OPENAI_API_KEY", ""),
        type="password"
    )
    if api_key:
        openai.api_key = api_key
    
    st.sidebar.divider()
    pages = {
        "📝 노트 & 도구": NotesAndToolsPage(),
        "🔗 위키백과": WikiPage(),
        "🤖 AI 조교": AIChatPage()
    }
    choice = st.sidebar.radio("메뉴", list(pages.keys()))
    st.sidebar.caption("✨ AI와 함께 수학을")
    pages[choice].run()

if __name__ == "__main__":
    main()
