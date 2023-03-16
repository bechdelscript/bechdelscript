from typing import Union

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from screenplay_classes import Script, Scene
import configue
from test_api.utils import Item, get_scenes_from_db, update_db


"""This script creates the API needed to link our backend and front end work."""

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
):
    """This first POST method called upload_script is used with a .txt file input, and returns
    the Bechdel score associated to this file aswell as the list of named characters and their gender.
    """
    filename = file.filename
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


# @app.get("/bechdel-scenes/{filename}")
# async def Bechdel_scenes(filename: str):
#     """This GET method returns the scenes that pass the highest score passed by the movie."""
#     score = db[filename]["score"]
#     if (score <= 1) and (score >= 0):
#         return {"message": "None of the scenes in the movie help pass the test."}
#     elif score == 2:
#         scenes = db[filename]["score_2"]
#         return {
#             "message": "The movie has two named female characters who speak together. Unfortunately, they do speak about men.",
#             "scenes": scenes,
#         }
#     elif score == 3:
#         scenes = db[filename]["score_3"]
#         return {"message": "The movie passes the Bechdel Test.", "scenes": scenes}
