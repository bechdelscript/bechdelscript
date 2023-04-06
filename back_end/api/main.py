from typing import Union
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from screenplay_classes import Script
import configue
from api.utils import (
    Item,
    update_db,
    get_scenes_from_db,
    get_scene_content,
    get_unique_random_user_key,
)


""" 
    This script creates the API needed to link our backend and front end work.
    Command to run uvicorn API : "uvicorn api.main:app --reload"
"""

config = configue.load("parameters.yaml")

app = FastAPI()
db = {}

origins = [
    "http://localhost:3000",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/upload-script/")
async def upload_script(
    background_task: BackgroundTasks,
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
        key = get_unique_random_user_key(db)
        background_task.add_task(
            upload_script_bg_task, content=content, config=config, key=key
        )
        return {"message": "The computations are launched", "key": key}
    else:
        return {"message": "There was an error uploading the file {}".format(filename)}


def upload_script_bg_task(content, config, key):
    response = Script(content, config)
    response.load_format()
    db[key] = update_db(response)


@app.get("/api/")
async def home():
    """This GET method is the basic method of our API."""
    return {"Message": "Welcome to the Bechdel Script Tester"}


@app.get("/api/list-scripts")
async def list_scripts():
    """This GET method returns the movie database over a run."""
    return {"Movies in base": db}


@app.get("/api/result-by-key/{key}")
async def result_by_title(key: int):
    """This GET method returns specific results based on a given user's key."""
    if key in db.keys():
        return {
            "message": "available",
            "score": db[key]["score"],
            "chars": db[key]["chars"],
            **get_scenes_from_db(key, db),
        }
    else:
        return {"message": "unavailable"}
        # raise HTTPException(404, f"Movie not in base")


@app.post("/api/result-with-user-gender-by-key/")
async def result_with_user_gender_by_title(
    item: Item, background_tasks: BackgroundTasks
):
    """This POST method returns specific results based on a given user's key and a dictionary of genders chosen by the user."""
    key = item.key
    user_gender = item.user_gender
    dico_gender = {k["name"]: k["gender"] for k in user_gender}
    config["bechdel_test_rules"][
        "only_women_in_whole_scene"
    ] = item.parameters.only_women_in_whole_scene
    config["bechdel_test_rules"][
        "whole_discussion_not_about_men"
    ] = item.parameters.whole_discussion_not_about_men
    if key in db.keys():
        temp = db[key]["script"]
        del db[key]
        background_tasks.add_task(
            result_with_user_gender_by_title_bg_task,
            temp=temp,
            dico_gender=dico_gender,
            key=key,
        )
        return {
            "message": "The computations are launched",
        }
    else:
        raise HTTPException(404, f"Movie not in base")


def result_with_user_gender_by_title_bg_task(temp, dico_gender, key):
    db[key] = update_db(temp, dico_gender)


@app.get("/api/content-scene/{key}/{scene_id}")
async def content_scene(key: int, scene_id: int):
    """This GET method returns the scene content given a user's key and scene id."""
    if key in db.keys():
        script = db[key]["script"]
        scene_content = get_scene_content(script, scene_id)
        return {"key": key, **scene_content}
    else:
        raise HTTPException(404, f"Movie not in base")

