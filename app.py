import streamlit as st

st.markdown("# login page")
st.markdown("### please input password")
UID = st.text_input("username")
passwd = st.text_input("password")
st.button("conform")
if st.button("conform"):
  break
