import streamlit as st
import openai
import base64
from datetime import datetime

# ---------- 페이지 설정 ----------
st.set_page_config(page_title="수학 학습 도우미", layout="wide")

# ---------- session_state 초기화 ----------
if "notes" not in st.session_state:
    st.session_state.notes = []  # 각 노트: {"text":..., "tags":[...], "time":...}
if "messages" not in st.session_state:
    st.session_state.messages = []  # 채팅 기록
if "ai_prompt" not in st.session_state:
    st.session_state.ai_prompt = ""  # 위키 페이지에서 전달된 질문
if "wiki_links" not in st.session_state:
    st.session_state.wiki_links = [
        {"title": "대수학", "url": "https://en.wikipedia.org/wiki/Algebra"},
        {"title": "기하학", "url": "https://en.wikipedia.org/wiki/Geometry"},
        {"title": "미적분학", "url": "https://en.wikipedia.org/wiki/Calculus"},
        {"title": "선형대수학", "url": "https://en.wikipedia.org/wiki/Linear_algebra"},
        {"title": "확률론", "url": "https://en.wikipedia.org/wiki/Probability_theory"},
    ]

if "basic_tags" not in st.session_state:
    st.session_state.basic_tags = [
        "대수학",
        "기하학",
        "미적분",
        "선형대수",
        "확률",
        "수론",
        "위상수학",
        "조합수학",
        "수학적 분석"
    ]

# ---------- 사이드바: 설정 및 메뉴 ----------
st.sidebar.title("📐 수학 학습 도우미")

page = st.sidebar.radio(
    "메뉴",
    ["📝 노트 및 태그", "🔗 위키백과 링크", "🤖 AI 대화"]
)

# OpenAI API Key
api_key = st.sidebar.text_input("OpenAI API Key 입력", type="password")

if api_key:
    openai.api_key = api_key


# ---------- 도구 함수 ----------
def image_to_base64(image_file):
    """업로드한 이미지를 base64 문자열로 변환"""
    return base64.b64encode(image_file.read()).decode("utf-8")


# ---------- 페이지1: 노트 및 태그 ----------
if page == "📝 노트 및 태그":

    st.header("📝 수학 노트")

    col1, col2 = st.columns([2, 1])

    with col1:

        note_text = st.text_area(
            "수학 노트를 작성하세요...",
            height=200
        )

        selected_basic_tags = st.multiselect(
            "기본 태그 선택",
            st.session_state.basic_tags
        )

        custom_tags_input = st.text_input(
            "사용자 정의 태그 (쉼표로 구분)",
            placeholder="예: 공식, 정리, 오답"
        )

        if st.button("노트 저장"):

            if note_text.strip():

                custom_tags = [
                    t.strip()
                    for t in custom_tags_input.split(",")
                    if t.strip()
                ]

                all_tags = selected_basic_tags + custom_tags

                st.session_state.notes.append(
                    {
                        "text": note_text,
                        "tags": all_tags,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                )

                st.success("노트가 저장되었습니다!")

            else:
                st.warning("노트 내용은 비워둘 수 없습니다.")


    with col2:

        st.subheader("모든 노트")

        if not st.session_state.notes:

            st.info("아직 노트가 없습니다. 첫 번째 노트를 작성해보세요!")

        else:

            for i, note in enumerate(reversed(st.session_state.notes)):

                with st.expander(
                    f"노트 {len(st.session_state.notes)-i} - {note['time']}"
                ):

                    st.markdown(note["text"])

                    if note["tags"]:
                        st.caption(
                            "태그: " + ", ".join(note["tags"])
                        )

                    if st.button("삭제", key=f"del_{i}"):

                        del st.session_state.notes[
                            len(st.session_state.notes)-1-i
                        ]

                        st.rerun()



# ---------- 페이지2: 위키백과 링크 ----------
elif page == "🔗 위키백과 링크":

    st.header("🔗 수학 개념 · 위키백과")

    st.caption(
        "버튼을 클릭하면 개념을 AI 대화 페이지로 보내 질문할 수 있습니다."
    )


    for i, link in enumerate(st.session_state.wiki_links):

        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            st.markdown(f"**{link['title']}**")

        with col2:
            st.markdown(
                f"[{link['url']}]({link['url']})"
            )

        with col3:

            if st.button("AI에게 질문", key=f"ask_{i}"):

                st.session_state.ai_prompt = (
                    f"이 수학 개념을 설명해주세요: {link['title']}, "
                    f"참고 링크: {link['url']}"
                )

                st.success(
                    "AI 대화 페이지로 전달되었습니다."
                )


    st.divider()

    st.subheader("➕ 나만의 위키 링크 추가")

    new_title = st.text_input(
        "개념 이름",
        placeholder="예: 푸리에 변환"
    )

    new_url = st.text_input(
        "위키백과 URL",
        placeholder="https://en.wikipedia.org/wiki/..."
    )


    if st.button("링크 추가"):

        if new_title and new_url:

            st.session_state.wiki_links.append(
                {
                    "title": new_title,
                    "url": new_url
                }
            )

            st.success("링크가 추가되었습니다.")

            st.rerun()

        else:

            st.warning(
                "모든 정보를 입력해주세요."
            )



# ---------- 페이지3: AI 대화 및 이미지 업로드 ----------
elif page == "🤖 AI 대화":

    st.header("🤖 AI 수학 튜터")


    if not api_key:

        st.warning(
            "먼저 사이드바에서 OpenAI API Key를 입력해주세요."
        )


    else:

        prompt_from_pg2 = st.session_state.ai_prompt


        if prompt_from_pg2:

            st.info(
                f"📋 위키 페이지에서 전달된 질문: {prompt_from_pg2}"
            )

            st.session_state.ai_prompt = ""


        for msg in st.session_state.messages:

            with st.chat_message(msg["role"]):

                st.markdown(msg["content"])



        with st.form(
            key="chat_form",
            clear_on_submit=True
        ):

            user_input = st.text_area(
                "수학 질문 입력",
                value=prompt_from_pg2,
                height=100,
                placeholder="예: 리만 가설을 설명해주세요..."
            )


            uploaded_image = st.file_uploader(
                "이미지 업로드 (선택 사항, 수식/문제 사진 지원)",
                type=["png", "jpg", "jpeg"]
            )


            submit_button = st.form_submit_button(
                "전송"
            )



        if submit_button and (
            user_input.strip()
            or uploaded_image
        ):

            if uploaded_image:

                base64_image = image_to_base64(
                    uploaded_image
                )

                image_url = (
                    f"data:image/jpeg;base64,{base64_image}"
                )


                user_message_content = [

                    {
                        "type": "text",
                        "text":
                        user_input
                        if user_input.strip()
                        else "이 이미지 속 수학 내용을 분석해주세요."
                    },

                    {
                        "type": "image_url",
                        "image_url":
                        {
                            "url": image_url
                        }
                    }

                ]

            else:

                user_message_content = user_input.strip()



            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": user_message_content
                }
            )


            with st.spinner("생각 중..."):

                try:

                    response = openai.ChatCompletion.create(
                        model="gpt-4o",
                        messages=st.session_state.messages,
                        max_tokens=1000
                    )


                    assistant_reply = (
                        response.choices[0]
                        .message.content
                    )


                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": assistant_reply
                        }
                    )


                    st.rerun()


                except Exception as e:

                    st.error(
                        f"오류 발생: {e}"
                    )


        if st.button("대화 기록 삭제"):

            st.session_state.messages = []

            st.rerun()
