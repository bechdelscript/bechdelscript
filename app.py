import streamlit as st
from io import StringIO


st.title("Welcome to Bechdel Tester !")
"Want to see if a film passes the bechdel test ? Upload its script !"
uploaded_file = st.file_uploader(
    label="Script.txt", accept_multiple_files=False, type=["txt"]
)
print(uploaded_file)


if uploaded_file is not None:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    string_data = stringio.read()
    st.write(string_data)
