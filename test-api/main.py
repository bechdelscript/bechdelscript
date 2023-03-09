from typing import Union

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from screenplay_classes import Script
import configue

config = configue.load("parameters.yaml")

app = FastAPI()
db = {}


@app.post("/upload_script/")
async def upload_script(
    file: UploadFile = File(...),
):
    filename = file.filename
    if file:
        content = await file.read()
        content = content.decode("unicode_escape").replace("\r", "")

        response = Script(content, config)
        response.load_format()
        response.bechdel()
        score = response.computed_score
        chars = [x for x in response.list_characters if x.is_named]
        db[filename] = {"score": score, "chars": chars}
        return {"message": "Fichier {} lu".format(filename)}
    else:
        return {"message": "There was an error uploading the file {}".format(filename)}


# /
@app.get("/")
async def home():
    return {"Message": "Welcome to the Bechdel Script Tester"}


# /list-scripts
@app.get("/list-scripts")
async def list_scripts():
    return {"Movies in base": db}


# c'est ici qu'il faut mettre la base des films. tous les titres?

# /result-by-title
@app.get("/result-by-title/{filename}")
async def result_by_title(filename: str):
    if filename in db.keys():
        return {"score": db[filename]["score"], "chars": db[filename]["chars"]}
    else:
        raise HTTPException(404, f"Movie not in base")


# /add-script
@app.post("/add-script")
async def add_script(filename: str):
    # db.append(filename)
    return {"message": f"added new script {filename} to DB"}
