from typing import Union

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from screenplay_classes import Script
import configue
import chardet

config = configue.load("parameters.yaml")

app = FastAPI()


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
        chars = response.list_characters
        return {
            "message": "Fichier {} lu".format(filename),
            "Score calculé": score,
            "Personnages": chars,
        }
    else:
        return {"message": "There was an error uploading the file {}".format(filename)}


# /
@app.get("/")
async def home():
    return {"Message": "Welcome to the Bechdel Script Tester"}


# /list-scripts
@app.get("/list-scripts")
async def list_scripts():
    return {"Movies in base": []}


# c'est ici qu'il faut mettre la base des films. tous les titres?

# /result-by-title
@app.get("/result-by-title/{filename}")
async def result_by_title(filename: str):
    # if filename dans le dossier
    # return {"result" : score quand on crée le script}
    # gérer cas où ça marche pas : raise HTTPException(404, f"Movie not in base")
    pass


# /add-script
@app.post("/add-script")
async def add_script(filename: str):
    # db.append(filename)
    return {"message": f"added new script {filename} to DB"}
