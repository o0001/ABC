import streamlit as st

with st.sidebar:
  st.header("프로필")
  user_name = st.text_input("닉네임")
  weather = st.selectbox("오늘 날씨", ["맑음","흐림","비/눈","매우 추움"])
  st.markdown("---")
  st.info(f"반가워요 {user_name}님! 오늘 날씨는'{weather}'이네요.")

st.title("👗 AI 코디 메이커")
st.write("사이드바에서 날씨를 먼저 선택하고 코디를 시작하세요")
st.header("👕 아이템 조합하기")

col1, col2 = st.tabs("상의","하의")
with col1:
  st.subheader("상의")
  top_type = st.radio("종류",["후드티","셔츠","맨투맨","반팔티셔츠"])
  top_color = st.select_slider("색상 톤",options=["밝음","무난함","어두움"])
with col2:
  st.subheader("하의")
  bottom_type = st.radio("종류",["청바지","슬랙스","트레이닝 팬츠","반바지"])
  bottom_color =st.select_slider("핏(fit)",options=["슬림","레귤러","오버핏"])
