import streamlit as st
st.markdown("# 앱 UI 만들기")
user_id = st.text_input("이름", placeholder="이름")
greade = st.radio("학년", ["1", "2", "3"], horizontal=True)
cls = st.number_input("반", value=1)
level = st.select_slider("난이도", ["쉬움","보통","어려움"])
num = st.slider("점수",0,100,50)
text = st.text_area("소감",placeholder="소감입니다.")
if st.button("질문 전송하기"):
    if agree:
        st.success(f" ({user_id})")
        st.markdown(f"""

        """)
        
        if age < 14:
            st.info("참고: 14세 미만 사용자이므로 보호자 모드가 활성화됩니다.")
    else:
        st.error("⚠️ 동의 항목에 체크해야 전송이 가능합니다.")
