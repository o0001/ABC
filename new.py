import streamlit as st
from openai import OpenAI

# OpenAI 클라이언트 초기화
ai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 세션 상태 초기화
if 'todo_list' not in st.session_state:
    st.session_state.todo_list = []
if 'user_motto' not in st.session_state:
    st.session_state.user_motto = "오늘도 화이팅!"
if 'motto_updated' not in st.session_state:
    st.session_state.motto_updated = False

def add_todo():
    task = st.session_state.get("todo_input", "").strip()
    if task:
        st.session_state.todo_list.append([task, False])
        st.toast("할 일이 추가되었습니다! 🚀")
        st.session_state.todo_input = ""
    else:
        st.toast("⚠️ 할 일을 입력해주세요!", icon="⚠️")

@st.dialog("오늘의 다짐 수정")
def edit_motto():
    motto = st.text_input("나의 한 줄 좌우명을 적어주세요.", value=st.session_state.user_motto)
    if st.button("다짐 저장"):
        if motto.strip():
            st.session_state.user_motto = motto
            st.session_state.motto_updated = True
            st.rerun()

def page_motto():
    st.header("📣 1. 오늘의 다짐")
    st.info(f"**현재 다짐:** {st.session_state.user_motto}")
    
    if st.button("다짐 수정하기"):
        edit_motto()
        
    if st.session_state.motto_updated:
        st.success("새로운 좌우명이 등록되었습니다!")
        st.session_state.motto_updated = False
        
    st.markdown("---")

def page_todo():
    st.header("✅ 2. 오늘의 할 일")
    st.write(f"현재 다짐: **{st.session_state.user_motto}**")
    
    # 입력 필드 및 버튼
    st.text_input("추가할 할 일을 입력하세요", key="todo_input", on_change=add_todo)
    st.button("추가하기", on_click=add_todo)
    
    st.markdown("---")
    
    if not st.session_state.todo_list:
        st.info("등록된 할 일이 없습니다. 새로운 할 일을 추가해보세요!")
    else:
        for i, (task, is_done) in enumerate(st.session_state.todo_list):
            col_task, col_btn, col_del = st.columns([4, 1, 1])
            
            with col_task:
                if is_done:
                    st.write(f"~{i+1}. {task}~ ✅")
                else:
                    st.write(f"{i+1}. {task}")
                    
            with col_btn:
                btn_label = "취소" if is_done else "완료"
                if st.button(btn_label, key=f"btn_toggle_{i}"):
                    st.session_state.todo_list[i][1] = not is_done
                    st.rerun()
                    
            with col_del:
                if st.button("삭제", key=f"btn_del_{i}"):
                    st.session_state.todo_list.pop(i)
                    st.rerun()
                    
    st.markdown("---")

def page_report():
    st.header("📈 3. 나의 갓생 지수")
    if not st.session_state.todo_list:
        st.write("아직 등록된 할 일이 없습니다.")
    else:
        total = len(st.session_state.todo_list)
        completed = sum(1 for item in st.session_state.todo_list if item[1])
        progress = (completed / total) * 100
        
        st.metric("오늘의 달성률", f"{progress:.1f}%", f"{completed}/{total} 완료")
        st.progress(progress / 100)
        
        if progress == 100:
            st.balloons()
            st.success("모든 목표를 달성하셨습니다! 🏆")
            
        st.markdown("---")
        if st.button("기록 전체 초기화", type="secondary"):
            st.session_state.todo_list = []
            st.rerun()

def page_ai_coach():
    st.header("🧐 AI 코치와 대화하기")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "너는 사용자의 할 일 목록과 달성 정도를 분석하여 조언하는 열정적인 코치야. 사용자가 더 멋진 삶을 살 수 있도록 명확한 조언과 응원을 해줘."}
        ]
        
    # 기존 대화 표시
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
    question = st.chat_input("AI 코치에게 질문해보세요!")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
            
        with st.chat_message("assistant"):
            # 현재 할 일 목록 context 구성
            todo_context = f"\n[현재 사용자 상태] 좌우명: '{st.session_state.user_motto}', 할 일: {st.session_state.todo_list}"
            
            # API 요청용 프롬프트 구성
            prompt = st.session_state.messages.copy()
            prompt[0] = {"role": "system", "content": st.session_state.messages[0]["content"] + todo_context}
            
            with st.spinner("AI 코치가 생각을 정리하고 있습니다...🤔"):
                response = ai_client.chat.completions.create(
                    model="gpt-4o-mini", # 유효한 OpenAI 모델명으로 변경
                    messages=prompt
                )
                ai_response = response.choices[0].message.content
                st.markdown(ai_response)
                
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

# 페이지 네비게이션 설정
pg = st.navigation([
    st.Page(page_motto, title="오늘의 다짐", icon="📣"),
    st.Page(page_todo, title="오늘의 할 일", icon="✅"),
    st.Page(page_report, title="나의 갓생 지수", icon="📈"),
    st.Page(page_ai_coach, title="AI 코칭", icon="🧐")
], position="top")

st.title("🌱 갓생 살기 플래너")
pg.run()
