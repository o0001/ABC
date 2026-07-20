import streamlit as st
with st.sidebar:
  st.header("프로필")
  user_name = st.text_input("닉네임")
  weather = st.selectbox("오늘 날씨", ["맑음","흐림","비/눈","매우 추움"])
  st.markdown("---")
  st.info(f"반가워요 {user_name}님! 오늘 날씨는'{weather}'이네요.")
st.title("👗 AI 코디 메이커")
st.write("사이드바에서 날씨를 먼저 선택하고 코디를 시작하세요")



