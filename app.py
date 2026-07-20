import streamlit as st

st.markdown("# login page")
st.markdown("### please input password")
UID = st.text_input("username")
passwd = st.text_input("password")
st.button("conform")
st.button("forgot your password? click here.")
