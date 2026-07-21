import streamlit as st
import openai
import base64
import os
from datetime import datetime
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
from abc import ABC, abstractmethod

# ---------- 페이지 기본 클래스 ----------
class PageBase(ABC):
    def __init__(self, title, icon):
        self.title = title
        self.icon = icon
    
    @abstractmethod
    def run(self):
        pass

# ---------- 세션 상태 초기화 ----------
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
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ---------- 유틸리티 함수 ----------
def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode("utf-8")

# ---------- 페이지 1: 노트 + 계산기 + 그래프 ----------
class NotesAndToolsPage(PageBase):
    def __init__(self):
        super().__init__("📝 노트 및 도구", "📝")
    
    def _note_section(self):
        st.subheader("✍️ 수학 노트")
        
        # ---- 수식 편집기 ----
        with st.expander("🧮 LaTeX 수식 편집기 (클릭하여 펼치기)", expanded=False):
            st.markdown("아래에 LaTeX 코드를 입력하면 실시간 미리보기가 가능하며, 자주 쓰는 기호를 빠르게 삽입할 수 있습니다.")
            col_btn, col_preview = st.columns([1, 3])
            with col_btn:
                # 빠른 기호 버튼
                symbols = [
                    ("분수", r"\frac{a}{b}"),
                    ("제곱근", r"\sqrt{x}"),
                    ("적분", r"\int_a^b"),
                    ("합계", r"\sum_{i=1}^n"),
                    ("극한", r"\lim_{x\to\infty}"),
                    ("행렬", r"\begin{pmatrix}a & b\\ c & d\end{pmatrix}"),
                    ("도함수", r"\frac{d}{dx}"),
                    ("편미분", r"\partial"),
                ]
                cols = st.columns(4)
                for i, (label, code) in enumerate(symbols):
                    with cols[i % 4]:
                        if st.button(label, key=f"sym_{i}"):
                            # LaTeX 조각을 입력창에 추가 (session_state를 통해 처리, 여기서는 간소화)
                            st.session_state.latex_input = st.session_state.get("latex_input", "") + code
                latex_code = st.text_area("LaTeX 코드", key="latex_input", height=80, 
                                        placeholder="예: \\int_{0}^{\\infty} e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}")
            with col_preview:
                if latex_code:
                    st.latex(latex_code)
                else:
                    st.info("미리보기 영역")
        
        # ---- 노트 입력 영역 ----
        col_text, col_image = st.columns([2, 1])
        with col_text:
            note_text = st.text_area("노트 텍스트 (Markdown 및 행내 LaTeX 지원, 예: $E=mc^2$)", height=150, 
                                     placeholder="Markdown과 LaTeX을 혼용할 수 있습니다:\n\n증명: $\\sum_{k=1}^{n} k = \\frac{n(n+1)}{2}$")
            # 수식 편집기에 내용이 있으면 자동으로 노트 끝에 추가
            if latex_code := st.session_state.get("latex_input", ""):
                st.caption("ℹ️ 수식 편집기에 추가된 LaTeX 수식은 노트 끝에 자동으로 첨부됩니다.")
        
        with col_image:
            uploaded_img = st.file_uploader("📷 이미지 삽입", type=["png", "jpg", "jpeg"], key="note_img")
            if uploaded_img:
                st.image(uploaded_img, caption="미리보기", width=200)
        
        # 태그 및 저장
        col1, col2 = st.columns([1, 1])
        with col1:
            selected_tags = st.multiselect("기본 태그", st.session_state.basic_tags)
        with col2:
            custom_input = st.text_input("사용자 정의 태그 (쉼표로 구분)", placeholder="공식, 정리")
        
        if st.button("💾 노트 저장", use_container_width=True):
            if note_text.strip() or uploaded_img or latex_code:
                # 이미지 처리
                img_base64 = None
                if uploaded_img:
                    img_base64 = image_to_base64(uploaded_img)
                
                # 전체 노트 내용 구성: LaTeX 수식을 텍스트 끝에 추가
                full_text = note_text
                if latex_code:
                    full_text += f"\n\n$$ {latex_code} $$"
                
                custom_tags = [t.strip() for t in custom_input.split(",") if t.strip()]
                all_tags = selected_tags + custom_tags
                
                st.session_state.notes.append({
                    "text": full_text,
                    "latex": latex_code if latex_code else None,
                    "image": img_base64,
                    "tags": all_tags,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("노트가 저장되었습니다!")
                # 임시 입력 초기화
                st.session_state.latex_input = ""
                st.rerun()
            else:
                st.warning("노트 내용, 이미지 또는 수식 중 하나 이상을 입력하세요.")
        
        # ---- 노트 목록 ----
        st.subheader("📚 기록 노트")
        if not st.session_state.notes:
            st.info("아직 노트가 없습니다. 첫 노트를 작성해보세요~")
        else:
            for idx, note in enumerate(reversed(st.session_state.notes)):
                real_idx = len(st.session_state.notes) - 1 - idx
                with st.expander(f"📌 {note['time']}  {', '.join(note['tags'])}"):
                    # 텍스트 표시 (Markdown + LaTeX 지원)
                    st.markdown(note["text"])
                    # 별도 수식이 있으면 다시 표시 (Markdown 렌더링 문제 방지)
                    if note.get("latex"):
                        st.latex(note["latex"])
                    # 이미지 표시
                    if note.get("image"):
                        st.image(base64.b64decode(note["image"]), caption="노트 이미지")
                    if st.button("🗑️ 삭제", key=f"del_note_{real_idx}"):
                        del st.session_state.notes[real_idx]
                        st.rerun()
    
    def _calculator_section(self):
        st.subheader("🧮 대수 계산기")
        with st.container(border=True):
            calc_type = st.selectbox("연산 유형", ["간소화", "미분", "적분", "방정식 풀이"])
            expr_str = st.text_input("수식 입력 (변수 x 사용)", value="x**2 + 2*x + 1", key="calc_input")
            x = sp.symbols('x')
            if st.button("🚀 계산", key="calc_btn"):
                try:
                    expr = sp.sympify(expr_str)
                    if calc_type == "간소화":
                        result = sp.simplify(expr)
                    elif calc_type == "미분":
                        result = sp.diff(expr, x)
                    elif calc_type == "적분":
                        result = sp.integrate(expr, x)
                    elif calc_type == "방정식 풀이":
                        if "=" in expr_str:
                            left, right = expr_str.split("=")
                            eq = sp.Eq(sp.sympify(left.strip()), sp.sympify(right.strip()))
                        else:
                            eq = sp.Eq(expr, 0)
                        result = sp.solve(eq, x)
                    st.success("계산 결과:")
                    st.latex(sp.latex(result))
                except Exception as e:
                    st.error(f"계산 오류: {e}")
    
    def _plot_section(self):
        st.subheader("📈 함수 그래프")
        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                func_str = st.text_input("f(x) =", value="sin(x)", key="plot_func")
            with col2:
                x_min = st.number_input("x 최소값", value=-5.0, key="xmin")
                x_max = st.number_input("x 최대값", value=5.0, key="xmax")
            if st.button("🎨 그래프 그리기", use_container_width=True):
                try:
                    x_sym = sp.symbols('x')
                    f = sp.lambdify(x_sym, sp.sympify(func_str), "numpy")
                    xs = np.linspace(x_min, x_max, 500)
                    ys = f(xs)
                    fig, ax = plt.subplots(figsize=(6, 3))
                    ax.plot(xs, ys, linewidth=2, color="#1f77b4")
                    ax.grid(True, linestyle="--", alpha=0.6)
                    ax.set_xlabel("x")
                    ax.set_ylabel("f(x)")
                    ax.set_title(f"y = {func_str}", fontweight="bold")
                    st.pyplot(fig)
                except Exception as e:
                    st.error(f"그래프 오류: {e}")
    
    def run(self):
        st.header(f"{self.icon} {self.title}")
        tab1, tab2, tab3 = st.tabs(["📝 노트", "🧮 계산기", "📈 그래프"])
        with tab1:
            self._note_section()
        with tab2:
            self._calculator_section()
        with tab3:
            self._plot_section()

# ---------- 페이지 2: 위키 링크 ----------
class WikiPage(PageBase):
    def __init__(self):
        super().__init__("위키백과 링크", "🔗")
    
    def run(self):
        st.header(f"{self.icon} 수학 개념 · 위키백과")
        st.markdown("오른쪽 버튼을 클릭하면 해당 개념을 AI 대화 페이지로 질문할 수 있습니다.")
        
        for i, link in enumerate(st.session_state.wiki_links):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{link['title']}**")
            with col2:
                st.markdown(f"[링크 열기 ↗]({link['url']})")
            with col3:
                if st.button("🤖 AI에게 물어보기", key=f"wiki_ask_{i}"):
                    st.session_state.ai_prompt = f"다음 수학 개념을 설명해주세요: {link['title']}，참고: {link['url']}"
                    st.toast("AI 대화 페이지로 전송됨", icon="📤")
        
        st.divider()
        st.subheader("➕ 사용자 정의 링크 추가")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                new_title = st.text_input("개념 이름", placeholder="푸리에 변환")
            with c2:
                new_url = st.text_input("위키백과 URL", placeholder="https://...")
            if st.button("✅ 링크 추가", use_container_width=True):
                if new_title and new_url:
                    st.session_state.wiki_links.append({"title": new_title, "url": new_url})
                    st.success("링크가 추가되었습니다.")
                    st.rerun()
                else:
                    st.warning("모든 정보를 입력해주세요.")

# ---------- 페이지 3: AI 대화 (표시 수정, ChatGPT 유사) ----------
class AIChatPage(PageBase):
    def __init__(self):
        super().__init__("AI 수학 조교", "🤖")
    
    def run(self):
        st.header(f"{self.icon} AI 수학 조교")
        if not openai.api_key:
            st.warning("유효한 OpenAI API Key를 사이드바에 입력해주세요.")
            return
        
        # 위키 페이지에서 전달된 질문 처리
        prompt = st.session_state.pop("ai_prompt", "")
        if prompt:
            st.info(f"📋 위키에서 온 질문: {prompt}")
        
        # ChatGPT 스타일을 위한 사용자 정의 CSS
        st.markdown("""
        <style>
        .chat-container {
            margin-bottom: 10px;
        }
        .user-msg {
            background-color: #dcf8c6;
            border-radius: 15px;
            padding: 10px 15px;
            margin: 5px 0;
            text-align: right;
            max-width: 80%;
            float: right;
            clear: both;
        }
        .assistant-msg {
            background-color: #f0f0f0;
            border-radius: 15px;
            padding: 10px 15px;
            margin: 5px 0;
            text-align: left;
            max-width: 80%;
            float: left;
            clear: both;
        }
        .clearfix::after {
            content: "";
            clear: both;
            display: table;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 채팅 기록 표시 (사용자 정의 HTML 버블)
        chat_html = '<div class="chat-container">'
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                content = msg["content"]
                # content가 리스트(이미지 포함)인 경우 텍스트 부분 추출
                if isinstance(content, list):
                    text_part = next((item["text"] for item in content if item["type"] == "text"), "")
                    chat_html += f'<div class="user-msg">{text_part}<br><small style="color:gray;">[이미지 포함]</small></div>'
                else:
                    chat_html += f'<div class="user-msg">{content}</div>'
            else:
                chat_html += f'<div class="assistant-msg">{msg["content"]}</div>'
        chat_html += '</div><div class="clearfix"></div>'
        st.markdown(chat_html, unsafe_allow_html=True)
        # 공식 st.chat_message를 대안으로 사용 가능 (위의 사용자 정의 블록을 주석 처리하고 아래 사용)
        # for msg in st.session_state.messages:
        #     with st.chat_message(msg["role"]):
        #         if isinstance(msg["content"], list):
        #             for part in msg["content"]:
        #                 if part["type"] == "text":
        #                     st.markdown(part["text"])
        #                 elif part["type"] == "image_url":
        #                     st.image(part["image_url"]["url"])
        #         else:
        #             st.markdown(msg["content"])
        
        # 입력 영역
        with st.form("chat_form", clear_on_submit=True):
            user_text = st.text_area("질문 입력", value=prompt, height=100, 
                                     placeholder="예: 리만 가설 설명, 이 적분 풀어주세요...")
            uploaded_img = st.file_uploader("📎 이미지 첨부 (선택)", type=["png", "jpg", "jpeg"])
            submitted = st.form_submit_button("📨 전송")
        
        if submitted and (user_text.strip() or uploaded_img):
            if uploaded_img:
                img_b64 = image_to_base64(uploaded_img)
                content = [
                    {"type": "text", "text": user_text if user_text.strip() else "이미지의 수학 내용을 분석해주세요"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            else:
                content = user_text.strip()
            
            st.session_state.messages.append({"role": "user", "content": content})
            
            with st.spinner("🤔 생각 중..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4o",
                        messages=st.session_state.messages,
                        max_tokens=1024,
                        temperature=0.7
                    )
                    reply = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.rerun()
                except Exception as e:
                    st.error(f"OpenAI 호출 실패: {e}")
        
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("🗑️ 대화 초기화", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

# ---------- 메인 프로그램 ----------
def main():
    st.set_page_config(page_title="수학 학습 도우미", page_icon="📐", layout="wide")
    
    st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { border-radius: 8px; }
    .stTextArea>label, .stTextInput>label { font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)
    
    init_session()
    
    # 사이드바 API Key
    st.sidebar.title("📐 수학 학습 도우미")
    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        value=os.environ.get("OPENAI_API_KEY", "[OPENAI_API_KEY]"),
        type="password",
        help="OpenAI API Key를 입력하거나 환경 변수 OPENAI_API_KEY를 설정하세요."
    )
    if api_key and api_key != "[OPENAI_API_KEY]":
        openai.api_key = api_key
    
    # 페이지 인스턴스
    pages = {
        "📝 노트 및 도구": NotesAndToolsPage(),
        "🔗 위키백과": WikiPage(),
        "🤖 AI 대화": AIChatPage()
    }
    
    selected = st.sidebar.radio("탐색", list(pages.keys()))
    st.sidebar.divider()
    st.sidebar.caption("AI와 도구로 수학을 쉽게 배우세요 ✨")
    
    pages[selected].run()

if __name__ == "__main__":
    main()
