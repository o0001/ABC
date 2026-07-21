import streamlit as st
import openai
import base64
import os
from datetime import datetime
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
from abc import ABC, abstractmethod
import uuid

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
        "system_prompt": "너는 친절한 수학 조교야. 답변은 간결하고 명확하게, 수식은 LaTeX로 표시해줘. 예: $E=mc^2$",
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
        ]
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
            
    for note in st.session_state.notes:
        if "id" not in note:
            note["id"] = str(uuid.uuid4())
            
    for link in st.session_state.wiki_links:
        if "id" not in link:
            link["id"] = str(uuid.uuid4())
            
    if "note_text" not in st.session_state:
        st.session_state.note_text = ""

def safe_image_to_base64(image_file):
    if image_file is None:
        return None
    return base64.b64encode(image_file.read()).decode("utf-8")

# ---------- LaTeX 심볼 도우미 ----------
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
                st.rerun()

# ---------- 페이지 1: 노트 + 계산기 + 그래프 ----------
class NotesAndToolsPage(PageBase):
    def __init__(self):
        super().__init__("📝 노트 & 도구", "📝")
    
    def run(self):
        st.header(f"{self.icon} {self.title}")
        
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
                    placeholder="""# 제목

피타고라스 정리:

$$a^2+b^2=c^2$$

미분 예:

$f'(x)=2x$"""
                )
            
            with col2:
                st.subheader("👀 실시간 미리보기")
                preview = st.session_state.get("note_text", "")
                
                preview_container = st.container(height=250, border=True)
                with preview_container:
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
                    st.session_state.note_text = ""
                    st.success("저장 완료")
                    st.rerun()
                else:
                    st.warning("내용이나 이미지를 입력하세요")
        
        # ---- 노트 필터링 & 목록 ----
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
                            new_text = st.text_area(
                                "내용",
                                value=note["text"],
                                key=f"edit_text_{note['id']}",
                                height=150
                            )
                            new_img = st.file_uploader("이미지 변경", type=["png","jpg","jpeg"], key=f"edit_img_{note['id']}")
                            if new_img:
                                st.image(new_img, width=150)
                            current_tags = note["tags"]
                            new_basic = st.multiselect(
                                "기본 태그",
                                st.session_state.basic_tags,
                                default=[t for t in current_tags if t in st.session_state.basic_tags],
                                key=f"edit_basic_{note['id']}"
                            )
                            new_custom = st.text_input(
                                "사용자 태그 (쉼표)",
                                value=", ".join([t for t in current_tags if t not in st.session_state.basic_tags]),
                                key=f"edit_custom_{note['id']}"
                            )
                            if st.button("수정 저장", key=f"save_edit_{note['id']}"):
                                note["text"] = new_text
                                if new_img:
                                    note["image"] = safe_image_to_base64(new_img)
                                note["tags"] = new_basic + [t.strip() for t in new_custom.split(",") if t.strip()]
                                st.success("수정 완료")
                                st.rerun()
                        else:
                            st.markdown(note["text"])
                            if note.get("image"):
                                st.image(base64.b64decode(note["image"]), width=250)
                        
                        if st.button("🗑 삭제", key=f"del_{note['id']}"):
                            st.session_state.notes = [n for n in st.session_state.notes if n["id"] != note["id"]]
                            st.rerun()
        
        st.divider()
        
        # ---- 계산기 & 그래프 ----
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

# ---------- 페이지 2: 위키 링크 ----------
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
                    st.session_state.wiki_links.append({
                        "id": str(uuid.uuid4()),
                        "title": title,
                        "url": url
                    })
                    st.success("추가됨")
                    st.rerun()
                else:
                    st.warning("모두 입력하세요")

# ---------- 페이지 3: 추천 강의 (3B1B, MIT, 만사침사록, Mathemaniac) ----------
class VideoPage(PageBase):
    def __init__(self):
        super().__init__("📺 추천 강의", "📺")
    
    def run(self):
        st.header(f"{self.icon} 추천 수학 강의 영상")
        st.caption("전 세계 최고 수준의 수학 시각화 및 대학원/교양 채널들을 만나보세요.")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "🔵 3Blue1Brown", 
            "🏛️ MIT OpenCourseWare", 
            "🇨🇳 만사침사록 (Meditation Math)", 
            "📐 Mathemaniac"
        ])
        
        with tab1:
            st.subheader("🎨 3Blue1Brown 핵심 시리즈")
            b3b1_videos = [
                {"title": "선형대수의 본질 (Essence of linear algebra)", "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab", "desc": "벡터, 행렬, 선형 변환의 기하학적 직관을 애니메이션으로 완벽히 이해하는 시리즈"},
                {"title": "미적분학의 본질 (Essence of calculus)", "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr", "desc": "도미노처럼 이어지는 미분과 적분의 개념적 본질을 명쾌하게 해설"},
                {"title": "신경망이란 무엇인가? (Neural Networks)", "url": "https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi", "desc": "딥러닝과 인공신경망의 수학적 원리를 시각적으로 파헤치는 입문 강의"}
            ]
            for v in b3b1_videos:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"### {v['title']}")
                        st.write(v['desc'])
                    with c2:
                        st.markdown(f"[🔗 재생목록 보기]({v['url']})")
                        if st.button("🤖 AI에게 질문", key=f"b3b_{v['title']}"):
                            st.session_state.ai_prompt = f"3Blue1Brown의 다음 강의 주제에 대해 설명해줘: {v['title']} ({v['desc']})"
                            st.toast("AI 조교 탭으로 전송되었습니다!")

        with tab2:
            st.subheader("🎓 MIT OpenCourseWare 수학 명강의")
            mit_videos = [
                {"title": "MIT 18.01 싱글 변수 미적분학 (Single Variable Calculus)", "url": "https://www.youtube.com/playlist?list=PLDespKuFfdEFt7xwMPgljQxX3gXy0p4oB", "desc": "미국 MIT의 정통 미적분학 강의로 극한, 도미노 미분법, 적분 응용을 깊이 있게 다룸"},
                {"title": "MIT 18.06 선형대수학 (Linear Algebra)", "url": "https://www.youtube.com/playlist?list=PLE7DDD91010BC51F8", "desc": "전설적인 교수 Gilbert Strang의 강의로 행렬 연산과 벡터 공간의 바이블"},
                {"title": "MIT 6.1200J 컴퓨터 과학을 위한 수학 (Mathematics for Computer Science)", "url": "https://www.youtube.com/playlist?list=PLUl4u3cNGP61VNvICqk2HXJTonnKgAc9d", "desc": "논리, 증명, 집합론, 그래프 이론 등 컴퓨터 과학의 뼈대가 되는 수학 강의"}
            ]
            for v in mit_videos:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"### {v['title']}")
                        st.write(v['desc'])
                    with c2:
                        st.markdown(f"[🔗 강의 시청하기]({v['url']})", unsafe_allow_html=True)
                        if st.button("🤖 AI에게 질문", key=f"mit_{v['title']}"):
                            st.session_state.ai_prompt = f"MIT 수학 강의 내용에 대해 설명해줘: {v['title']} ({v['desc']})"
                            st.toast("AI 조교 탭으로 전송되었습니다!")

        with tab3:
            st.subheader("🇨🇳 만사침사록 (Meditation Math) 플레이리스트")
            manshi_videos = [
                {"title": "漫士数学 플레이리스트 (Meditation Math)", "url": "https://www.youtube.com/playlist?list=PLShBlXb7zxehR3ebOvob3_S01lPepc84-", "desc": "인공신경망, 딥러닝, 기하학적 통찰 등 깊이 있는 수학적 개념을 직관적으로 탐구하는 시리즈"}
            ]
            for v in manshi_videos:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"### {v['title']}")
                        st.write(v['desc'])
                    with c2:
                        st.markdown(f"[🔗 재생목록 보기]({v['url']})")
                        if st.button("🤖 AI에게 질문", key=f"manshi_{v['title']}"):
                            st.session_state.ai_prompt = f"만사침사록의 수학/AI 콘텐츠 주제에 대해 설명해줘: {v['title']} ({v['desc']})"
                            st.toast("AI 조교 탭으로 전송되었습니다!")

        with tab4:
            st.subheader("📐 Mathemaniac 플레이리스트")
            mathemaniac_videos = [
                {"title": "Essence of complex analysis", "url": "https://www.youtube.com/playlist?list=PLDcSwjT2BF_UDdkQ3KQjX5SRQ2DLLwv0R", "desc": "복소해석학의 핵심 원리를 명쾌하고 아름답게 시각화한 시리즈"},
                {"title": "Traditional topics, explained in a new way", "url": "https://www.youtube.com/playlist?list=PLDcSwjT2BF_WVum1CMO9hMSIa7TyrGjsK", "desc": "기존의 수학 주제들을 완전히 새로운 시각과 방법으로 풀어낸 플레이리스트"},
                {"title": "Essence of differential forms", "url": "https://www.youtube.com/playlist?list=PLDcSwjT2BF_XBTtg1vNbsWZbx0WPK09GI", "desc": "미분형식(Differential Forms)의 본질을 직관적으로 이해할 수 있는 고급 수학 시리즈"},
                {"title": "Essence of Group Theory", "url": "https://www.youtube.com/playlist?list=PLDcSwjT2BF_VuNbn8HiHZKKy59SgnIAeO", "desc": "추상대수학의 기초인 군론(Group Theory)의 개념적 본질을 다루는 시리즈"}
            ]
            for v in mathemaniac_videos:
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown(f"### {v['title']}")
                        st.write(v['desc'])
                    with c2:
                        st.markdown(f"[🔗 재생목록 보기]({v['url']})")
                        if st.button("🤖 AI에게 질문", key=f"mathemaniac_{v['title']}"):
                            st.session_state.ai_prompt = f"Mathemaniac 채널의 다음 강의 주제에 대해 설명해줘: {v['title']} ({v['desc']})"
                            st.toast("AI 조교 탭으로 전송되었습니다!")

# ---------- 페이지 4: AI 대화 ----------
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
        
        for msg in st.session_state.messages:
            if msg["role"] == "system":
                continue
            with st.chat_message(msg["role"]):
                if isinstance(msg["content"], list):
                    for part in msg["content"]:
                        if part["type"] == "text":
                            st.markdown(part["text"])
                        elif part["type"] == "image_url":
                            st.image(part["image_url"]["url"], width=200)
                else:
                    st.markdown(msg["content"])
        
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([5, 1])
            with col1:
                user_text = st.text_area("질문", value=prompt, height=80,
                                         placeholder="수학 질문을 입력하세요", key="chat_input")
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
                
                sys_prompt = st.session_state.get("system_prompt", "")
                if sys_prompt and (len(st.session_state.messages) == 0 or st.session_state.messages[0]["role"] != "system"):
                    st.session_state.messages.insert(0, {"role": "system", "content": sys_prompt})
                
                st.session_state.messages.append({"role": "user", "content": content})
                
                with st.spinner("생각 중..."):
                    try:
                        client = openai.OpenAI(api_key=openai.api_key)
                        resp = client.chat.completions.create(
                            model="gpt-4o",
                            messages=st.session_state.messages,
                            max_tokens=1024,
                            temperature=0.7
                        )
                        reply = resp.choices[0].message.content
                        st.session_state.messages.append({"role": "assistant", "content": reply})
                        st.rerun()
                    except Exception as e:
                        st.error(f"OpenAI 오류: {e}")
            else:
                st.warning("질문을 입력하세요")
        
        if st.button("🗑 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

# ---------- 메인 ----------
def main():
    st.set_page_config(page_title="수학 도우미", page_icon="📐", layout="wide")
    st.markdown("""
    <style>
        .stApp { background: #fafafa; }
        .stButton>button { border-radius: 8px; font-weight: 500; transition: 0.2s; }
        .stButton>button:hover { background-color: #eef6ff; border-color: #90caf9; }
        .stTextArea textarea { border-radius: 8px; }
        .stExpander { border: 1px solid #e0e0e0; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)
    
    init_session()
    
    st.sidebar.title("📐 수학 도우미")
    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        value=os.environ.get("OPENAI_API_KEY", ""),
        type="password"
    )
    if api_key:
        openai.api_key = api_key
    
    st.sidebar.divider()
    st.sidebar.subheader("🤖 AI 시스템 프롬프트")
    new_prompt = st.sidebar.text_area(
        "AI 역할 지정",
        value=st.session_state.system_prompt,
        height=100,
        help="AI에게 원하는 역할과 답변 방식을 알려주세요."
    )
    if new_prompt != st.session_state.system_prompt:
        st.session_state.system_prompt = new_prompt
        if st.session_state.messages and st.session_state.messages[0]["role"] == "system":
            st.session_state.messages[0]["content"] = new_prompt
    
    pages = {
        "📝 노트 & 도구": NotesAndToolsPage(),
        "🔗 위키백과": WikiPage(),
        "📺 추천 강의": VideoPage(),
        "🤖 AI 조교": AIChatPage()
    }
    choice = st.sidebar.radio("메뉴", list(pages.keys()))
    st.sidebar.caption("✨ AI와 함께 수학을")
    pages[choice].run()

if __name__ == "__main__":
    main()
