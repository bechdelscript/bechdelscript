import streamlit as st
from io import StringIO
import yaml

from screenplay_classes import Script

config = yaml.safe_load(open("parameters.yaml"))

st.title("Welcome to Bechdel Tester !")
"Want to see if a film passes the bechdel test ? Upload its script !"
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

    script = Script(script_text=string_data, config=config)
    script.load_format()
    script.bechdel()

    if st.button("Test !"):
        # script = Script.from_path(
        #     script_path="data/input/scripts_imsdb/His-Girl-Friday.txt", config=config
        # )

        # st.write("Nombres de scènes :", len(script.list_scenes))
        st.write("Nombres de personnages :", len(script.list_characters))

        gender_dict, submit = script.display_results_streamlit(3)

        if submit:
            gender_dict = {
                k: "m"
                if v == "Male"
                else "f"
                if v == "Female"
                else "nb"
                if v == "Non Binary"
                else None
                for k, v in gender_dict.items()
            }

            print(gender_dict)
            script.bechdel(user_genders=gender_dict)
            # gender_dict, submit = script.display_results_streamlit(3)
