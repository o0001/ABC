import streamlit as st
st.title("카운터 앱")
count = 0
if st.button("증가"):
  count = count + 1
st.markdown(f"## 현제 숫자:`{count}`")
