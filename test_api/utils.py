from screenplay_classes import Script, Scene
from pydantic import BaseModel


class Item(BaseModel):
    filename: str
    user_gender: list


def update_db(script: Script, user_gender: dict = None):
    script.bechdel(user_gender)
    score = script.computed_score
    score_2 = script.score2_scenes
    score_3 = script.score3_scenes
    chars = [x for x in script.list_characters if x.is_named]
    return {
        "score": score,
        "chars": chars,
        "script": script,
        "score_2": score_2,
        "score_3": score_3,
    }
