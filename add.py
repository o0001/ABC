import streamlit as st
st.title("카운터 앱")
if 'count' not in st. session_state:
  st.session_state.count = 1
if st.button("증가"):
  st.session_state.count += 1
  st.session_state.A = 10 ** st.session_state.count
  st.markdown(f"## 현제 숫자:`{st.session_state.A}`")
