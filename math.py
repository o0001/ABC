import streamlit as st
import openai
import base64
import os
import json
from datetime import datetime, timedelta
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
from abc import ABC, abstractmethod
import uuid
import pandas as pd
import plotly.express as px

# ---------- 数据文件 ----------
DATA_FILE = "math_data.json"

# ---------- 基类 ----------
class PageBase(ABC):
    def __init__(self, title, icon):
        self.title = title
        self.icon = icon
    @abstractmethod
    def run(self):
        pass

# ---------- 数据持久化 ----------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ---------- 会话初始化 ----------
def init_session():
    defaults = {
        "notes": [],
        "messages": [],
        "ai_prompt": "",
        "system_prompt": (
            "너는 친절하고 유능한 수학 조교야. "
            "답변은 간결하고 명확하게, 수식은 LaTeX로 표시해줘. 예: $E=mc^2$."
        ),
        "wiki_links": [
            {"id": str(uuid.uuid4()), "title": "대수학", "url": "https://en.wikipedia.org/wiki/Algebra"},
            {"id": str(uuid.uuid4()), "title": "기하학", "url": "https://en.wikipedia.org/wiki/Geometry"},
            {"id": str(uuid.uuid4()), "title": "미적분학", "url": "https://en.wikipedia.org/wiki/Calculus"},
            {"id": str(uuid.uuid4()), "title": "선형대수학", "url": "https://en.wikipedia.org/wiki/Linear_algebra"},
            {"id": str(uuid.uuid4()), "title": "확률론", "url": "https://en.wikipedia.org/wiki/Probability_theory"},
            {"id": str(uuid.uuid4()), "title": "정수론", "url": "https://en.wikipedia.org/wiki/Number_theory"},
            {"id": str(uuid.uuid4()), "title": "군론", "url": "https://en.wikipedia.org/wiki/Group_theory"},
            {"id": str(uuid.uuid4()), "title": "환론", "url": "https://en.wikipedia.org/wiki/Ring_theory"},
            {"id": str(uuid.uuid4()), "title": "체론", "url": "https://en.wikipedia.org/wiki/Field_(mathematics)"},
            {"id": str(uuid.uuid4()), "title": "위상수학", "url": "https://en.wikipedia.org/wiki/Topology"},
            {"id": str(uuid.uuid4()), "title": "미분기하학", "url": "https://en.wikipedia.org/wiki/Differential_geometry"},
            {"id": str(uuid.uuid4()), "title": "대수기하학", "url": "https://en.wikipedia.org/wiki/Algebraic_geometry"},
            {"id": str(uuid.uuid4()), "title": "조합론", "url": "https://en.wikipedia.org/wiki/Combinatorics"},
            {"id": str(uuid.uuid4()), "title": "그래프 이론", "url": "https://en.wikipedia.org/wiki/Graph_theory"},
            {"id": str(uuid.uuid4()), "title": "게임 이론", "url": "https://en.wikipedia.org/wiki/Game_theory"},
            {"id": str(uuid.uuid4()), "title": "수리논리학", "url": "https://en.wikipedia.org/wiki/Mathematical_logic"},
            {"id": str(uuid.uuid4()), "title": "집합론", "url": "https://en.wikipedia.org/wiki/Set_theory"},
            {"id": str(uuid.uuid4()), "title": "범주론", "url": "https://en.wikipedia.org/wiki/Category_theory"},
            {"id": str(uuid.uuid4()), "title": "복소해석학", "url": "https://en.wikipedia.org/wiki/Complex_analysis"},
            {"id": str(uuid.uuid4()), "title": "실해석학", "url": "https://en.wikipedia.org/wiki/Real_analysis"},
            {"id": str(uuid.uuid4()), "title": "함수해석학", "url": "https://en.wikipedia.org/wiki/Functional_analysis"},
            {"id": str(uuid.uuid4()), "title": "편미분방정식", "url": "https://en.wikipedia.org/wiki/Partial_differential_equation"},
            {"id": str(uuid.uuid4()), "title": "상미분방정식", "url": "https://en.wikipedia.org/wiki/Ordinary_differential_equation"},
            {"id": str(uuid.uuid4()), "title": "푸리에 변환", "url": "https://en.wikipedia.org/wiki/Fourier_transform"},
            {"id": str(uuid.uuid4()), "title": "라플라스 변환", "url": "https://en.wikipedia.org/wiki/Laplace_transform"},
            {"id": str(uuid.uuid4()), "title": "수치해석", "url": "https://en.wikipedia.org/wiki/Numerical_analysis"},
            {"id": str(uuid.uuid4()), "title": "최적화", "url": "https://en.wikipedia.org/wiki/Mathematical_optimization"},
            {"id": str(uuid.uuid4()), "title": "선형계획법", "url": "https://en.wikipedia.org/wiki/Linear_programming"},
            {"id": str(uuid.uuid4()), "title": "통계학", "url": "https://en.wikipedia.org/wiki/Statistics"},
            {"id": str(uuid.uuid4()), "title": "베이지안 통계", "url": "https://en.wikipedia.org/wiki/Bayesian_statistics"},
            {"id": str(uuid.uuid4()), "title": "머신러닝 수학", "url": "https://en.wikipedia.org/wiki/Mathematics_of_machine_learning"},
            {"id": str(uuid.uuid4()), "title": "카오스 이론", "url": "https://en.wikipedia.org/wiki/Chaos_theory"},
            {"id": str(uuid.uuid4()), "title": "프랙탈", "url": "https://en.wikipedia.org/wiki/Fractal"},
            {"id": str(uuid.uuid4()), "title": "황금비", "url": "https://en.wikipedia.org/wiki/Golden_ratio"},
            {"id": str(uuid.uuid4()), "title": "수학적 귀납법", "url": "https://en.wikipedia.org/wiki/Mathematical_induction"},
            {"id": str(uuid.uuid4()), "title": "소수", "url": "https://en.wikipedia.org/wiki/Prime_number"},
            {"id": str(uuid.uuid4()), "title": "리만 가설", "url": "https://en.wikipedia.org/wiki/Riemann_hypothesis"}
        ],
        "basic_tags": [
            "대수학", "기하학", "미적분학", "선형대수학",
            "확률", "정수론", "위상수학", "조합론",
            "수리해석", "군론", "해석학", "미분방정식",
            "통계학", "최적화", "수치해석", "논리학",
            "그래프이론", "머신러닝수학"
        ],
        "flashcards": [],          # {"id","question","answer","tags","repetition","interval","efactor","next_review"}
        "mistakes": [],            # {"id","problem","user_answer","correct_answer","explanation","tags","time"}
        "practice_history": []     # {"topic","score","time"}
    }
    # 从文件加载已有数据，覆盖默认值
    saved = load_data()
    for k, v in saved.items():
        if k in defaults:
            defaults[k] = v
    # 初始化 session_state
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    # 兼容旧数据（无id字段时补上）
    for note in st.session_state.notes:
        if "id" not in note:
            note["id"] = str(uuid.uuid4())
    for link in st.session_state.wiki_links:
        if "id" not in link:
            link["id"] = str(uuid.uuid4())
    for card in st.session_state.flashcards:
        if "id" not in card:
            card["id"] = str(uuid.uuid4())
    for m in st.session_state.mistakes:
        if "id" not in m:
            m["id"] = str(uuid.uuid4())
    # 输入框状态
    if "note_text" not in st.session_state:
        st.session_state.note_text = ""

def persist():
    """将关键数据写入 JSON 文件"""
    data_to_save = {
        "notes": st.session_state.notes,
        "wiki_links": st.session_state.wiki_links,
        "flashcards": st.session_state.flashcards,
        "mistakes": st.session_state.mistakes,
        "practice_history": st.session_state.practice_history,
    }
    save_data(data_to_save)

# ---------- 工具函数 ----------
def safe_image_to_base64(image_file):
    if image_file is None:
        return None
    return base64.b64encode(image_file.read()).decode("utf-8")

def latex_symbol_buttons(target_key="note_text"):
    cols = st.columns(5)
    symbols = [
        ("분수", r"$\frac{a}{b}$"),
        ("제곱근", r"$\sqrt{x}$"),
        ("적분", r"$\int_{a}^{b}$"),
        ("합", r"$\sum_{i=1}^{n}$"),
        ("극한", r"$\lim_{x\to\infty}$"),
        ("행렬", r"$\begin{pmatrix}a & b\\ c & d\end{pmatrix}$"),
        ("미분", r"$\frac{d}{dx}$"),
        ("편미분", r"$\partial$"),
        ("무한대", r"$\infty$"),
        ("화살표", r"$\rightarrow$"),
        ("시그마", r"$\sigma$"),
        ("델타", r"$\Delta$"),
        ("파이", r"$\pi$"),
        ("세타", r"$\theta$"),
        ("람다", r"$\lambda$"),
        ("오메가", r"$\omega$"),
    ]
    for i, (name, code) in enumerate(symbols):
        with cols[i % 5]:
            if st.button(name, key=f"sym_{target_key}_{i}", use_container_width=True):
                st.session_state[target_key] = st.session_state.get(target_key, "") + code

def generate_markdown_export(content_list, title="수학 자료"):
    md = f"# {title}\n\n"
    for item in content_list:
        if "text" in item:  # 笔记
            md += f"### {item.get('time','')}  {', '.join(item.get('tags',[]))}\n\n"
            md += item["text"] + "\n\n"
        elif "role" in item:  # 对话
            role = item["role"]
            if role == "system":
                continue
            content = item.get("content", "")
            if isinstance(content, list):
                texts = [p.get("text","") for p in content if p.get("type")=="text"]
                content = " ".join(texts)
            md += f"**{role}**: {content}\n\n"
    return md

# ---------- AI 工具定义 ----------
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_wiki_link",
            "description": "사용자가 요청한 수학 관련 웹사이트 링크나 유튜브 플레이리스트를 위키/링크 목록에 추가합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "링크 또는 채널/플레이리스트의 제목"},
                    "url": {"type": "string", "description": "웹사이트 또는 유튜브 재생목록 URL"}
                },
                "required": ["title", "url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_note",
            "description": "사용자가 정리해달라고 한 수학 공식이나 내용을 노트에 자동으로 저장합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "노트에 저장할 마크다운 및 LaTeX 형식의 내용"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "관련 태그 목록"}
                },
                "required": ["text"]
            }
        }
    }
]

def execute_tool_call(name, args_str):
    try:
        args = json.loads(args_str)
    except:
        args = {}
    if name == "add_wiki_link":
        title = args.get("title", "제목 없음")
        url = args.get("url", "")
        st.session_state.wiki_links.append({
            "id": str(uuid.uuid4()),
            "title": title,
            "url": url
        })
        persist()
        return f"'{title}' 링크가 위키 목록에 추가되었습니다!"
    elif name == "add_note":
        text = args.get("text", "")
        tags = args.get("tags", ["AI생성"])
        st.session_state.notes.append({
            "id": str(uuid.uuid4()),
            "text": text,
            "image": None,
            "tags": tags,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        persist()
        return "새로운 노트가 저장되었습니다!"
    return "알 수 없는 도구입니다."

# ---------- 各页面实现 ----------

class NotesAndToolsPage(PageBase):
    def __init__(self):
        super().__init__("📝 노트 & 도구", "📝")
    
    def run(self):
        st.header(f"{self.icon} {self.title}")
        # 新笔记
        with st.container(border=True):
            st.subheader("✍️ 새 노트")
            st.caption("버튼을 클릭해 LaTeX 기호를 쉽게 입력하세요")
            latex_symbol_buttons("note_text")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("✍️ 작성")
                st.text_area(
                    "Markdown + LaTeX",
                    key="note_text",
                    height=250,
                    placeholder="""# 제목\n\n피타고라스 정리:\n$$a^2+b^2=c^2$$\n\n미분 예:\n$f'(x)=2x$"""
                )
            with col2:
                st.subheader("👀 실시간 미리보기")
                preview = st.session_state.get("note_text", "")
                with st.container(height=250, border=True):
                    if preview.strip():
                        st.markdown(preview)
                    else:
                        st.info("왼쪽에 입력하면 여기에 표시됩니다.")
            img = st.file_uploader("참고 이미지 첨부", type=["png", "jpg", "jpeg"], key="new_note_img")
            if img:
                st.image(img, width=200)
            tags = st.multiselect("기본 태그", st.session_state.basic_tags, default=[], placeholder="선택", key="new_note_tags")
            custom_tags = st.text_input("사용자 태그 (쉼표)", placeholder="공식, 정리", key="new_note_custom_tags")
            if st.button("💾 저장", use_container_width=True):
                note_text = st.session_state.get("note_text", "")
                if note_text.strip() or img:
                    b64 = safe_image_to_base64(img)
                    all_tags = tags + [t.strip() for t in custom_tags.split(",") if t.strip()]
                    st.session_state.notes.append({
                        "id": str(uuid.uuid4()),
                        "text": note_text,
                        "image": b64,
                        "tags": all_tags,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    persist()
                    st.session_state.note_text = ""
                    st.success("저장 완료")
                    st.rerun()
                else:
                    st.warning("내용이나 이미지를 입력하세요")
        
        # 笔记列表、筛选、编辑
        st.subheader("📚 기록")
        if not st.session_state.notes:
            st.info("아직 노트가 없어요")
        else:
            with st.expander("🔍 필터", expanded=False):
                filter_tags = st.multiselect("태그로 필터", st.session_state.basic_tags, key="filter_tags")
                col_date1, col_date2 = st.columns(2)
                with col_date1:
                    start_date = st.date_input("시작 날짜", value=None, key="start_date")
                with col_date2:
                    end_date = st.date_input("종료 날짜", value=None, key="end_date")
            filtered = []
            for note in st.session_state.notes:
                if filter_tags:
                    if not any(tag in note["tags"] for tag in filter_tags):
                        continue
                note_date = datetime.strptime(note["time"], "%Y-%m-%d %H:%M").date()
                if start_date and note_date < start_date:
                    continue
                if end_date and note_date > end_date:
                    continue
                filtered.append(note)
            if not filtered:
                st.info("조건에 맞는 노트가 없습니다")
            else:
                for note in reversed(filtered):
                    with st.expander(f"📌 {note['time']}  {', '.join(note['tags'])}"):
                        edit_key = f"edit_{note['id']}"
                        if edit_key not in st.session_state:
                            st.session_state[edit_key] = False
                        edit_mode = st.checkbox("편집 모드", key=f"toggle_{note['id']}")
                        if edit_mode:
                            st.caption("내용 수정 (버튼을 눌러 LaTeX 기호 추가)")
                            latex_symbol_buttons(f"edit_text_{note['id']}")
                            new_text = st.text_area("내용", value=note["text"], key=f"edit_text_{note['id']}", height=150)
                            new_img = st.file_uploader("이미지 변경", type=["png","jpg","jpeg"], key=f"edit_img_{note['id']}")
                            if new_img:
                                st.image(new_img, width=150)
                            current_tags = note["tags"]
                            new_basic = st.multiselect("기본 태그", st.session_state.basic_tags,
                                                       default=[t for t in current_tags if t in st.session_state.basic_tags],
                                                       key=f"edit_basic_{note['id']}")
                            new_custom = st.text_input("사용자 태그 (쉼표)",
                                                       value=", ".join([t for t in current_tags if t not in st.session_state.basic_tags]),
                                                       key=f"edit_custom_{note['id']}")
                            if st.button("수정 저장", key=f"save_edit_{note['id']}"):
                                note["text"] = new_text
                                if new_img:
                                    note["image"] = safe_image_to_base64(new_img)
                                note["tags"] = new_basic + [t.strip() for t in new_custom.split(",") if t.strip()]
                                persist()
                                st.success("수정 완료")
                                st.rerun()
                        else:
                            st.markdown(note["text"])
                            if note.get("image"):
                                st.image(base64.b64decode(note["image"]), width=250)
                        if st.button("🗑 삭제", key=f"del_{note['id']}"):
                            st.session_state.notes = [n for n in st.session_state.notes if n["id"] != note["id"]]
                            persist()
                            st.rerun()
        
        # 导出按钮
        if st.button("📥 모든 노트 마크다운으로 내보내기"):
            md = generate_markdown_export(st.session_state.notes, "수학 노트")
            st.download_button("마크다운 다운로드", md, file_name="notes.md")
        
        st.divider()
        # 计算器与绘图
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
                            C = sp.Symbol('C')
                            res = sp.integrate(e, x) + C
                        else:
                            if "=" in expr:
                                l, r = expr.split("=")
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
                        xs = np.linspace(xmin, xmax, 500)
                        ys = f(xs)
                        fig, ax = plt.subplots(figsize=(5,3))
                        ax.plot(xs, ys, color="#2b8cbe")
                        ax.grid(True, linestyle="--", alpha=0.5)
                        ax.set_xlabel("x"); ax.set_ylabel("f(x)")
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"오류: {e}")

class WikiPage(PageBase):
    def __init__(self):
        super().__init__("🔗 위키백과", "🔗")
    def run(self):
        st.header(f"{self.icon} 수학 개념 위키")
        st.caption("개념을 선택하면 AI에게 질문할 수 있어요")
        for link in st.session_state.wiki_links:
            cols = st.columns([3, 2, 1])
            with cols[0]:
                st.markdown(f"**{link['title']}**")
            with cols[1]:
                st.markdown(f"[바로가기]({link['url']})")
            with cols[2]:
                if st.button("🤖 질문", key=f"wiki_{link['id']}"):
                    st.session_state.ai_prompt = f"다음 개념을 설명해줘: {link['title']} (참고: {link['url']})"
                    st.toast("AI 대화로 전송됨")
        st.divider()
        st.subheader("➕ 링크 추가")
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("이름", placeholder="푸리에 변환")
            with c2:
                url = st.text_input("URL", placeholder="https://...")
            if st.button("추가", use_container_width=True):
                if title and url:
                    st.session_state.wiki_links.append({"id": str(uuid.uuid4()), "title": title, "url": url})
                    persist()
                    st.success("추가됨")
                    st.rerun()
                else:
                    st.warning("모두 입력하세요")

class VideoPage(PageBase):
    def __init__(self):
        super().__init__("📺 추천 강의", "📺")
    def run(self):
        st.header(f"{self.icon} 추천 수학 강의 영상")
        st.caption("전 세계 최고 수준의 수학 시각화 및 대학원/교양 채널들을 만나보세요.")
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔵 3Blue1Brown", 
            "🏛️ MIT OCW", 
            "🇨🇳 만사침사록", 
            "📐 Mathemaniac",
            "🔬 Veritasium"   # 新增
        ])
        with tab1:
            st.subheader("🎨 3Blue1Brown 핵심 시리즈")
            videos = [
                ("선형대수의 본질", "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab"),
                ("미적분학의 본질", "https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr"),
                ("신경망이란?", "https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi")
            ]
            for title, url in videos:
                with st.container(border=True):
                    c1, c2 = st.columns([3,1])
                    with c1:
                        st.markdown(f"**{title}**")
                    with c2:
                        st.markdown(f"[재생목록]({url})")
                        if st.button("🤖 AI에게 질문", key=f"b3b_{title}"):
                            st.session_state.ai_prompt = f"{title} 강의에 대해 설명해줘 ({url})"
                            st.toast("AI 조교로 전송")
        with tab2:
            st.subheader("🎓 MIT OCW")
            videos = [
                ("18.01 단일변수 미적분", "https://www.youtube.com/playlist?list=PLDespKuFfdEFt7xwMPgljQxX3gXy0p4oB"),
                ("18.06 선형대수", "https://www.youtube.com/playlist?list=PLE7DDD91010BC51F8"),
                ("6.1200J 컴퓨터과학 수학", "https://www.youtube.com/playlist?list=PLUl4u3cNGP61VNvICqk2HXJTonnKgAc9d")
            ]
            for title, url in videos:
                with st.container(border=True):
                    c1, c2 = st.columns([3,1])
                    with c1:
                        st.markdown(f"**{title}**")
                    with c2:
                        st.markdown(f"[강의]({url})")
                        if st.button("🤖 AI에게 질문", key=f"mit_{title}"):
                            st.session_state.ai_prompt = f"MIT {title} 강의 내용 설명해줘 ({url})"
                            st.toast("AI 조교로 전송")
        with tab3:
            st.subheader("🇨🇳 만사침사록 (Meditation Math)")
            videos = [("漫士数学 플레이리스트", "https://www.youtube.com/playlist?list=PLShBlXb7zxehR3ebOvob3_S01lPepc84-")]
            for title, url in videos:
                with st.container(border=True):
                    c1, c2 = st.columns([3,1])
                    with c1:
                        st.markdown(f"**{title}**")
                    with c2:
                        st.markdown(f"[재생목록]({url})")
                        if st.button("🤖 AI에게 질문", key=f"manshi_{title}"):
                            st.session_state.ai_prompt = f"만사침사록의 수학/AI 콘텐츠 설명해줘: {title} ({url})"
                            st.toast("AI 조교로 전송")
        with tab4:
            st.subheader("📐 Mathemaniac")
            videos = [
                ("Essence of complex analysis", "https://www.youtube.com/playlist?list=PLDcSwjT2BF_UDdkQ3KQjX5SRQ2DLLwv0R"),
                ("Traditional topics, new way", "https://www.youtube.com/playlist?list=PLDcSwjT2BF_WVum1CMO9hMSIa7TyrGjsK"),
                ("Essence of differential forms", "https://www.youtube.com/playlist?list=PLDcSwjT2BF_XBTtg1vNbsWZbx0WPK09GI"),
                ("Essence of Group Theory", "https://www.youtube.com/playlist?list=PLDcSwjT2BF_VuNbn8HiHZKKy59SgnIAeO")
            ]
            for title, url in videos:
                with st.container(border=True):
                    c1, c2 = st.columns([3,1])
                    with c1:
                        st.markdown(f"**{title}**")
                    with c2:
                        st.markdown(f"[재생목록]({url})")
                        if st.button("🤖 AI에게 질문", key=f"mathe_{title}"):
                            st.session_state.ai_prompt = f"Mathemaniac 강의 {title} 설명해줘 ({url})"
                            st.toast("AI 조교로 전송")
        with tab5:
            st.subheader("🔬 Veritasium (真理元素)")
            videos = [
                ("Veritasium 主频道", "https://www.youtube.com/@veritasium"),
                ("Veritasium 数学相关播放列表", "https://www.youtube.com/playlist?list=PLkahZjV5wKe-Z1RP3ZiYwe8JSAolmqF9M"),
            ]
            for title, url in videos:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"**{title}**")
                    with c2:
                        st.markdown(f"[바로가기]({url})")
                        if st.button("🤖 AI에게 질문", key=f"veritasium_{title}"):
                            st.session_state.ai_prompt = f"Veritasium 채널의 {title} 내용에 대해 설명해줘 ({url})"
                            st.toast("AI 조교로 전송")

class SkillAssessmentPage(PageBase):
    def __init__(self):
        super().__init__("📊 숙련도 진단", "📊")
    def run(self):
        st.header(f"{self.icon} 학습자 숙련도 및 진단 분석")
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.subheader("🎯 적응형 퀴즈")
                if st.button("레벨 테스트", use_container_width=True):
                    st.session_state.ai_prompt = "내 수학 실력 진단을 위해 적응형 퀴즈 문제를 내줘."
                    st.toast("AI 조교 탭으로 이동")
        with col2:
            with st.container(border=True):
                st.subheader("🔗 선수 학습 체크포인트")
                st.write("- 선형대수: 미완료")
                st.write("- 편미분: 미완료")
                if st.button("체크 실행", use_container_width=True):
                    st.session_state.ai_prompt = "고급 개념 학습 전 필요한 선수 학습 체크포인트 테스트를 진행해줘."
                    st.toast("AI 조교 탭으로 이동")
        with st.container(border=True):
            st.subheader("📈 행동 기반 프로파일")
            st.write(f"- 노트 수: {len(st.session_state.notes)}")
            st.write(f"- 링크 수: {len(st.session_state.wiki_links)}")
            st.write(f"- 카드 수: {len(st.session_state.flashcards)}")

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
        # 显示消息
        for msg in st.session_state.messages:
            role = msg.get("role")
            if role == "system" or role == "tool":
                continue
            with st.chat_message("user" if role == "user" else "assistant"):
                content = msg.get("content", "")
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict):
                            if part.get("type") == "text":
                                st.markdown(part.get("text", ""))
                            elif part.get("type") == "image_url":
                                url = part.get("image_url", {}).get("url", "")
                                if url:
                                    st.image(url, width=200)
                else:
                    st.markdown(content)
        # 输入
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([5, 1])
            with col1:
                user_text = st.text_area("질문", value=prompt, height=80, placeholder="질문을 입력하세요", key="chat_input")
            with col2:
                uploaded = st.file_uploader("📎", type=["png","jpg","jpeg"], label_visibility="collapsed")
            submitted = st.form_submit_button("전송")
        if submitted:
            if user_text.strip() or uploaded:
                if uploaded:
                    b64 = safe_image_to_base64(uploaded)
                    content = [
                        {"type": "text", "text": user_text if user_text.strip() else "이미지 분석해줘"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                    ]
                else:
                    content = user_text.strip()
                # 确保 system prompt 存在
                if not any(m.get("role") == "system" for m in st.session_state.messages):
                    st.session_state.messages.insert(0, {"role": "system", "content": st.session_state.system_prompt})
                st.session_state.messages.append({"role": "user", "content": content})
                with st.spinner("생각 중..."):
                    try:
                        client = openai.OpenAI(api_key=openai.api_key)
                        response = client.chat.completions.create(
                            model="gpt_5.4_mini",
                            messages=st.session_state.messages,
                            tools=tools,
                            tool_choice="auto",
                            max_tokens=1024,
                            temperature=0.7
                        )
                        msg = response.choices[0].message
                        if msg.tool_calls:
                            # 保存助手消息
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": msg.content,
                                "tool_calls": [
                                    {"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                                    for tc in msg.tool_calls
                                ]
                            })
                            for tc in msg.tool_calls:
                                result = execute_tool_call(tc.function.name, tc.function.arguments)
                                st.session_state.messages.append({
                                    "role": "tool",
                                    "tool_call_id": tc.id,
                                    "name": tc.function.name,
                                    "content": result
                                })
                            # 再次调用
                            resp2 = client.chat.completions.create(
                                model="gpt-4o",
                                messages=st.session_state.messages,
                                max_tokens=1024,
                                temperature=0.7
                            )
                            reply = resp2.choices[0].message.content
                        else:
                            reply = msg.content
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                        st.rerun()
                    except Exception as e:
                        st.error(f"오류: {e}")
            else:
                st.warning("질문을 입력하세요")
        if st.button("🗑 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        # 导出对话
        if st.button("📥 대화 내보내기 (Markdown)"):
            md = generate_markdown_export(st.session_state.messages, "AI 대화 기록")
            st.download_button("다운로드", md, file_name="chat.md")

class FlashcardPage(PageBase):
    def __init__(self):
        super().__init__("🔄 플래시카드", "🔄")
    def sm2_update(self, card, quality):
        if quality < 3:
            card["repetition"] = 0
            card["interval"] = 1
        else:
            if card["repetition"] == 0:
                card["interval"] = 1
            elif card["repetition"] == 1:
                card["interval"] = 6
            else:
                card["interval"] = int(card["interval"] * card["efactor"])
            card["repetition"] += 1
        card["efactor"] = max(1.3, card["efactor"] + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        card["next_review"] = (datetime.now() + timedelta(days=card["interval"])).strftime("%Y-%m-%d")
        return card
    def run(self):
        st.header(f"{self.icon} 복습 카드")
        tab1, tab2 = st.tabs(["📋 복습하기", "➕ 카드 생성"])
        with tab1:
            today = datetime.now().strftime("%Y-%m-%d")
            due = [c for c in st.session_state.flashcards if c.get("next_review", "2000-01-01") <= today]
            if not due:
                st.success("오늘 복습할 카드가 없습니다!")
            else:
                if "current_card_idx" not in st.session_state:
                    st.session_state.current_card_idx = 0
                idx = st.session_state.current_card_idx % len(due)
                card = due[idx]
                with st.container(border=True):
                    st.markdown("### 질문")
                    st.write(card["question"])
                    show = st.checkbox("정답 보기")
                    if show:
                        st.markdown("### 정답")
                        st.write(card["answer"])
                        quality = st.slider("이해도 (0~5)", 0, 5, 3, key="quality")
                        if st.button("다음 카드"):
                            updated = self.sm2_update(card, quality)
                            for i, c in enumerate(st.session_state.flashcards):
                                if c["id"] == card["id"]:
                                    st.session_state.flashcards[i] = updated
                                    break
                            persist()
                            st.session_state.current_card_idx = (idx + 1) % len(due)
                            st.rerun()
        with tab2:
            st.subheader("노트에서 카드 자동 생성")
            if st.button("AI로 카드 생성 요청"):
                st.session_state.ai_prompt = "선택한 노트를 바탕으로 플래시카드 질문-답변 쌍을 만들어줘."
                st.info("AI 조교 페이지에서 질문을 전송해주세요")
            st.divider()
            st.subheader("수동 추가")
            q = st.text_area("질문", key="fc_q")
            a = st.text_area("답변", key="fc_a")
            tags = st.text_input("태그 (쉼표)")
            if st.button("카드 저장"):
                if q and a:
                    st.session_state.flashcards.append({
                        "id": str(uuid.uuid4()),
                        "question": q,
                        "answer": a,
                        "tags": [t.strip() for t in tags.split(",") if t.strip()],
                        "repetition": 0,
                        "interval": 1,
                        "efactor": 2.5,
                        "next_review": datetime.now().strftime("%Y-%m-%d")
                    })
                    persist()
                    st.success("추가됨!")
                    st.session_state.fc_q = ""
                    st.session_state.fc_a = ""
                else:
                    st.warning("모두 입력하세요")

class PracticePage(PageBase):
    def __init__(self):
        super().__init__("✏️ 연습 문제", "✏️")
    def run(self):
        st.header(f"{self.icon} 연습 & 오답")
        tab1, tab2, tab3 = st.tabs(["📝 문제 생성", "📋 풀기", "📕 오답 노트"])
        with tab1:
            topic = st.selectbox("주제", st.session_state.basic_tags)
            diff = st.radio("난이도", ["초급","중급","고급"], horizontal=True)
            if st.button("문제 생성 요청"):
                st.session_state.ai_prompt = f"{topic} 분야 {diff} 난이도 수학 문제를 하나 만들어줘."
                st.info("AI 조교 탭에서 질문을 전송해주세요")
        with tab2:
            prob = st.text_area("문제", height=100)
            user_ans = st.text_input("내 답")
            correct = st.text_input("정답")
            expl = st.text_area("해설")
            if st.button("제출 및 채점"):
                if prob and user_ans:
                    if user_ans.strip() != correct.strip():
                        st.session_state.mistakes.append({
                            "id": str(uuid.uuid4()),
                            "problem": prob,
                            "user_answer": user_ans,
                            "correct_answer": correct,
                            "explanation": expl,
                            "tags": [],
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                        })
                        persist()
                        st.error("오답! 오답 노트에 저장됨.")
                    else:
                        st.success("정답!")
                    st.session_state.practice_history.append({
                        "topic": "미분류",
                        "score": 1 if user_ans.strip() == correct.strip() else 0,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    persist()
        with tab3:
            if not st.session_state.mistakes:
                st.info("오답 없음")
            else:
                for m in reversed(st.session_state.mistakes):
                    with st.expander(f"{m['time']} - {m['problem'][:30]}..."):
                        st.write("문제:", m["problem"])
                        st.write("내 답:", m["user_answer"])
                        st.write("정답:", m["correct_answer"])
                        st.write("해설:", m["explanation"])
                        if st.button("삭제", key=f"del_m_{m['id']}"):
                            st.session_state.mistakes.remove(m)
                            persist()
                            st.rerun()

class DashboardPage(PageBase):
    def __init__(self):
        super().__init__("📊 대시보드", "📊")
    def run(self):
        st.header(f"{self.icon} 학습 대시보드")
        # 标签分布饼图
        tag_counts = {}
        for note in st.session_state.notes:
            for tag in note.get("tags", []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        if tag_counts:
            fig = px.pie(values=list(tag_counts.values()), names=list(tag_counts.keys()), title="노트 태그 분포")
            st.plotly_chart(fig, use_container_width=True)
        # 每日笔记趋势
        dates = [datetime.strptime(n["time"], "%Y-%m-%d %H:%M").date() for n in st.session_state.notes]
        if dates:
            df = pd.DataFrame({"날짜": dates})
            df2 = df.groupby("날짜").size().reset_index(name="노트 수")
            fig2 = px.line(df2, x="날짜", y="노트 수", title="날짜별 노트 작성 추이")
            st.plotly_chart(fig2, use_container_width=True)
        total_cards = len(st.session_state.flashcards)
        due_cards = sum(1 for c in st.session_state.flashcards if c.get("next_review","2000-01-01") <= datetime.now().strftime("%Y-%m-%d"))
        col1, col2 = st.columns(2)
        with col1:
            st.metric("총 플래시카드", total_cards)
        with col2:
            st.metric("오늘 복습할 카드", due_cards)

# ---------- 主函数 ----------
def main():
    st.set_page_config(page_title="수학 도우미", page_icon="📐", layout="wide")
    st.markdown("""
    <style>
        .stApp { background: #fafafa; }
        .stButton>button { border-radius: 8px; font-weight: 500; }
        .stTextArea textarea { border-radius: 8px; }
        .stExpander { border: 1px solid #e0e0e0; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)
    init_session()
    st.sidebar.title("📐 수학 도우미")
    api_key = st.sidebar.text_input("OpenAI API Key", value=os.environ.get("OPENAI_API_KEY", ""), type="password")
    if api_key:
        openai.api_key = api_key
    st.sidebar.divider()
    st.sidebar.subheader("🤖 AI 시스템 프롬프트")
    new_prompt = st.sidebar.text_area("AI 역할 지정", value=st.session_state.system_prompt, height=100)
    if new_prompt != st.session_state.system_prompt:
        st.session_state.system_prompt = new_prompt
        # 更新现有 system 消息
        for m in st.session_state.messages:
            if m.get("role") == "system":
                m["content"] = new_prompt
                break
    pages = {
        "📝 노트 & 도구": NotesAndToolsPage(),
        "🔗 위키백과": WikiPage(),
        "📺 추천 강의": VideoPage(),
        "📊 숙련도 진단": SkillAssessmentPage(),
        "🤖 AI 조교": AIChatPage(),
        "🔄 플래시카드": FlashcardPage(),
        "✏️ 연습 문제": PracticePage(),
        "📊 대시보드": DashboardPage()
    }
    choice = st.sidebar.radio("메뉴", list(pages.keys()))
    st.sidebar.caption("✨ AI와 함께 수학을")
    pages[choice].run()

if __name__ == "__main__":
    main()
