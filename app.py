import streamlit as st
from io import StringIO
import yaml

from screenplay_classes import Script

config = yaml.safe_load(open("parameters.yaml"))

st.title("Welcome to Bechdel Tester !")
st.write("Want to see if a film passes the bechdel test ? Upload its script !")
uploaded_file = st.file_uploader(
    label="Upload script here :", accept_multiple_files=False, type=["txt"]
)

if uploaded_file:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    string_data = stringio.read()

    if st.button("Show script"):
        if st.button("Hide script"):
            pass
        st.write(string_data)

    if st.button("Test !"):
        script = Script(script_text=string_data, config=config)
        script.load_format()
        script.bechdel()

        script.display_results_streamlit(nb_scenes=3)
