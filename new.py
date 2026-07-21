import streamlit as st

# Initialize Session State
if 'todo_list' not in st.session_state:
    st.session_state.todo_list = []
if 'user_motto' not in st.session_state:
    st.session_state.user_motto = "오늘도 화이팅!"

def add_todo():
    task = st.session_state.todo_input.strip()
    if task:
        st.session_state.todo_list.append([task, False])
        st.toast("할 일이 추가되었습니다!")
        st.session_state.todo_input = ""  # Clear input
    else:
        st.toast("⚠️ 할 일을 입력해주세요!", icon="⚠️")

def page_1():
    st.title("🌱 갓생 살기 플래너")
    st.header("📣 1. 오늘의 다짐")
    
    # FIX: Pre-fill with current motto
    motto = st.text_input("나의 한 줄 좌우명을 적어주세요", value=st.session_state.user_motto)
    
    if st.button("다짐 저장"):
        if motto.strip():
            st.session_state.user_motto = motto
            st.success("좌우명이 등록되었습니다!")
        else:
            st.warning("좌우명을 입력해주세요!")
    st.markdown("---")

def page_2():
    st.header("✅ 2. 오늘의 할 일")
    st.write(f"현재 다짐: **{st.session_state.user_motto}**")
    
    st.text_input("추가할 할 일을 입력하세요", key="todo_input")
    st.button("추가하기", on_click=add_todo)

    st.markdown("---")
    
    for i, item in enumerate(st.session_state.todo_list):
        col_task, col_btn, col_status = st.columns([4, 1, 1])
        with col_task:
            st.write(f"{i+1}. {item[0]}")
        with col_btn:
            # FIX: Toggle status (True <-> False) instead of only setting to True
            btn_label = "취소" if item[1] else "완료"
            if st.button(btn_label, key=f"btn_{i}"):
                st.session_state.todo_list[i][1] = not st.session_state.todo_list[i][1]
                st.rerun()
        with col_status:
            if item[1]:
                st.write("✅ **달성!**")
    st.markdown("---")

def page_3():
    st.header("📈 3. 나의 갓생 지수")
    if not st.session_state.todo_list:
        st.write("아직 등록된 할 일이 없습니다.")
    else:
        total = len(st.session_state.todo_list)
        count = sum(1 for item in st.session_state.todo_list if item[1])
        
        progress_ratio = count / total
        st.metric("오늘의 달성률", f"{progress_ratio * 100:.1f}%")
        st.progress(progress_ratio)
        
        if st.button("기록 전체 초기화"):
            st.session_state.todo_list = []
            st.rerun()

pg = st.navigation([
    st.page(page_1, title="오늘의 다짐"),
    st.page(page_2, title="오늘의 할 일"),
    st.page(page_3, title="나의 갓생 지수")
])
pg.run()
