from typing import Union

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from screenplay_classes import Script
import configue
from api.utils import Item, update_db, get_scenes_from_db, get_scene_content


""" 
    This script creates the API needed to link our backend and front end work.
    Command to run uvicorn API : "uvicorn api.main:app --reload"
"""

config = configue.load("parameters.yaml")

app = FastAPI()
db = {}

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload-script/")
async def upload_script(
    file: UploadFile = File(...),
    only_women_in_whole_scene: bool = Form(),
    whole_discussion_not_about_men: bool = Form(),
):
    """This first POST method called upload_script is used with a .txt file input, and returns
    the Bechdel score associated to this file aswell as the list of named characters and their gender.
    """
    filename = file.filename
    config["bechdel_test_rules"][
        "only_women_in_whole_scene"
    ] = only_women_in_whole_scene
    config["bechdel_test_rules"][
        "whole_discussion_not_about_men"
    ] = whole_discussion_not_about_men
    if file:
        content = await file.read()
        content = content.decode("unicode_escape").replace("\r", "")

        response = Script(content, config)
        response.load_format()
        db[filename] = update_db(response)
        return {
            "message": "Fichier {} lu".format(filename),
            "score": db[filename]["score"],
            "chars": db[filename]["chars"],
            **get_scenes_from_db(filename, db),
        }
    else:
        return {"message": "There was an error uploading the file {}".format(filename)}


@app.get("/")
async def home():
    """This GET method is the basic method of our API."""
    return {"Message": "Welcome to the Bechdel Script Tester"}


@app.get("/list-scripts")
async def list_scripts():
    """This GET method returns the movie database over a run."""
    return {"Movies in base": db}


@app.get("/result-by-title/{filename}")
async def result_by_title(filename: str):
    """This GET method returns specific results based on a given filename."""
    if filename in db.keys():
        return {"score": db[filename]["score"], "chars": db[filename]["chars"]}
    else:
        raise HTTPException(404, f"Movie not in base")


@app.post("/result-with-user-gender-by-title/")
async def result_with_user_gender_by_title(item: Item):
    """This POST method returns specific results based on a given filename and a dictionary of genders chosen by the user."""
    filename = item.filename
    user_gender = item.user_gender
    dico_gender = {k["name"]: k["gender"] for k in user_gender}
    config["bechdel_test_rules"][
        "only_women_in_whole_scene"
    ] = item.parameters.only_women_in_whole_scene
    config["bechdel_test_rules"][
        "whole_discussion_not_about_men"
    ] = item.parameters.whole_discussion_not_about_men
    if filename in db.keys():
        temp = db[filename]["script"]
        db[filename] = update_db(temp, dico_gender)
        return {
            "score": db[filename]["score"],
            "chars": db[filename]["chars"],
            **get_scenes_from_db(filename, db),
        }
    else:
        raise HTTPException(404, f"Movie not in base")


@app.get("/content-scene/{filename}/{scene_id}")
async def content_scene(filename: str, scene_id: int):
    """This GET method returns the scene content given a filename and scene id."""
    if filename in db.keys():
        script = db[filename]["script"]
        scene_content = get_scene_content(script, scene_id)
        return {"filename": filename, **scene_content}
    else:
        raise HTTPException(404, f"Movie not in base")
