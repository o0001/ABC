import streamlit as st

st.markdown("# login page")
st.markdown("### please input password")
UID = st.text_input("username")
passwd = st.text_input("password")
if st.button("conform"):
  if UID == "123":
    if passwd == "123":
      st.success("ture")
  else:
    st.error("wrong user id or password")
