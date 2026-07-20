import streamlit as st
st.header("👕 아이템 조합하기")
col1, col2 = st.colums(2)
with col1:
  st.subheader("상의")
  top_type = st.radio("종류",["후드티","셔츠","",""])
  top_color = st.select_slider("색상 톤",options=["","",""])
with col2:
  st.subheader("하의")
  bottom_type = st.radio("종류",["","","",""])
  bottom_color =st.select_slider("핏(fit)",optiins=["","",""])
