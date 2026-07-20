import streamlit as st
st.header("👕 아이템 조합하기")
col1, col2 = st.colums(2)
with col1:
  st.subheader("상의")
  top_type = st.radio()
  top_color = st.select_slider()
with col2:
  st.subheader
  bottom_type
  bottom_color
