from typing import Union

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from screenplay_classes import Script
import configue


"""This script creates the API needed to link our backend and front end work."""

config = configue.load("parameters.yaml")

app = FastAPI()
db = {}


@app.post("/upload-script/")
async def upload_script(
    file: UploadFile = File(...),
):
    """This first POST method called upload_script is used with a .txt file input, and returns
    the Bechdel score associated to this file aswell as the list of named characters and their gender."""
    filename = file.filename
    if file:
        content = await file.read()
        content = content.decode("unicode_escape").replace("\r", "")

        response = Script(content, config)
        response.load_format()
        response.bechdel()
        score = response.computed_score
        chars = [x for x in response.list_characters if x.is_named]
        db[filename] = {"score": score, "chars": chars, "script": response}
        return {
            "message": "Fichier {} lu".format(filename),
            "score": score,
            "chars": chars,
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


@app.get("/result-with-user-gender-by-title/{filename}")
async def result_with_user_gender_by_title(filename: str, user_gender: dict):
    """This GET method returns specific results based on a given filename and a dictionary of genders chosen by the user."""
    if filename in db.keys():
        temp = db[filename]["script"]
        temp.bechdel(user_gender)
        score = temp.computed_score
        chars = [x for x in temp.list_characters if x.is_named]
        db[filename] = {"score": score, "chars": chars, "script": temp}
        return {"score": score, "chars": chars}
    else:
        raise HTTPException(404, f"Movie not in base")
