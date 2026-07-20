import streamlit as st

def reset_all():
  st.session_state.user_name = ""
  st.session_state.weather = "맑음"
  st.session_state.top_type = "후드티"
  st.session_state.top_color = "밝음"
  st.session_state.bottom_type = "청바지"
  st.session_state.bottom_color = "슬림"
  st.session_state.shoes = "스니커즈"
  st.session_state.acc = []
  
with st.sidebar:
  st.header("프로필")
  user_name = st.text_input("닉네임")
  weather = st.selectbox("오늘 날씨", ["맑음","흐림","비/눈","매우 추움"])
  st.markdown("---")
  st.info(f"반가워요 {user_name}님! 오늘 날씨는'{weather}'이네요.")

st.title("👗 AI 코디 메이커")
st.write("사이드바에서 날씨를 먼저 선택하고 코디를 시작하세요")
st.header("👕 아이템 조합하기")

col1, col2 = st.columns(2)
with col1:
  st.subheader("상의")
  top_type = st.radio("종류",["후드티","셔츠","맨투맨","반팔티셔츠"])
  top_color = st.select_slider("색상 톤",options=["밝음","무난함","어두움"])
with col2:
  st.subheader("하의")
  bottom_type = st.radio("종류",["청바지","슬랙스","트레이닝 팬츠","반바지"])
  bottom_color =st.select_slider("핏(fit)",options=["슬림","레귤러","오버핏"])
  
st.header("디테일 추가")
tab1, tab2 = st.tabs(["신발", "액세서리"])

with tab1:
    st.write("오늘의 발걸음을 책임질 신발:")
    shoes = st.selectbox("신발 선택", ["스니커즈", "운동화", "구두", "슬리퍼"])
    with st.expander("신발 선택 팁 보기"):
        st.info("너무 튀는 신발은 지양하도록 해요!")

with tab2:
    st.write("포인트 아이템:")
    acc = st.multiselect("액세서리 추가", ["모자", "안경", "목걸이", "가방"])
    with st.expander("액세서리 스타일링 팁 보기"):
        st.warning("너무 많은 액세서리는 투머치가 될 수 있어요.")
st.markdown("---")
if st.button("코디 완성하기"):
  with st.container(border=1):
    st.subheader(f"{user_name}님의 오늘의 룩북")
    st.write(f"오늘같은 **{weather}** 날씨에는 이렇게 입어보세요!")
    st.markdown(f"""
    * **상의**{top_color}{top_type}
    * **하의**{bottom_color}{bottom_type}
    * **매칭**{shoes}와{','.join(acc) if acc else '아세서리 없이 깔끔하게'}
    """)
    st.success("오늘의 스타이링이 와성되었읍니다! 자신 있게 외출하세요!")
    
    with st.expander("코디 연출 팁 영상보기"):
      st.video("https://www.youtube.com/watch?v=_E1cYx6P2h4")
      st.write("전문가가 제안하는 코디 연출법을 참고해 보세요")
    
st.button("전체 초기화",on_click=reset_all())
