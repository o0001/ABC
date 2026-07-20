import streamlit as st
import time

def reset_game():
    st.session_state.start_time = 0
    st.session_state.end_time = 0
    st.session_state.result = 0
if 'start_time' not in st.session_state:
    reset_game()

st.title("10초 맞추기 게임!")
st.write("시작 버튼을 누르고, 마음속으로 10초를 센 뒤 종료 버튼을 누르세요.")

col1, col2 = st.columns(2)
with col1:
    if st.button("시작"):
        st.session_state.start_time = time.time() # 현재 시각 기록
        st.session_state.end_time = 0          # 종료 시간 초기화
with col2:
    if st.button("종료"):
        if st.session_state.start_time != 0:
            st.session_state.end_time = time.time()
            # 걸린 시간 계산 (종료 시간 - 시작 시간)
            st.session_state.result = st.session_state.end_time - st.session_state.start_time
        else:
            st.warning("시작 버튼을 먼저 눌러주세요!")

if st.session_state.end_time != 0:
    diff = st.session_state.result
    st.header(f"결과: {diff:.2f}초") # 소수점 둘째자리까지 표시
    # 성공 판정 (9.7초 ~ 10.3초 사이)
    if 9.7 <= diff <= 10.3:
        st.success("대단해요! 정확합니다!")
    else:
        st.error(f"10초와 {abs(10-diff):.2f}초 차이가 납니다. 다시 도전해보세요!")

st.button("다시 하기", on_click=reset_game)
