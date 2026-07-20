import streamlit as st
st.header("👕 아이템 조합하기")
col1, col2 = st.columns(2)
with col1:
  st.subheader("상의")
  top_type = st.radio("종류",["후드티","셔츠","","반팔티셔츠"])
  top_color = st.select_slider("색상 톤",options=["밝음","무난함","어두움"])
with col2:
  st.subheader("하의")
  bottom_type = st.radio("종류",["청바지","슬랙스","트레이닝 팬츠","반바지"])
  bottom_color =st.select_slider("핏(fit)",optiins=["슬림","레귤러","오버핏"])
