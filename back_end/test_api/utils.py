from screenplay_classes import Script, Scene
from pydantic import BaseModel


class Parameters(BaseModel):
    only_women_in_whole_scene: bool  # these two parameters can take values (true, true), (true, false), (false, false)
    whole_discussion_not_about_men: bool


class Item(BaseModel):
    filename: str
    user_gender: list
    parameters: Parameters


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


def get_scenes_from_db(filename: str, db):
    score = db[filename]["score"]
    if (score <= 1) and (score >= 0):
        return {
            "message_result": "None of the scenes in the movie help pass the test.",
            "scenes": [],
        }
    elif score == 2:
        scenes = db[filename]["score_2"]
        return {
            "message_result": "The movie has two named female characters who speak together. Unfortunately, they do speak about men.",
            "scenes": scenes,
        }
    elif score == 3:
        scenes = db[filename]["score_3"]
        return {
            "message_result": "The movie passes the Bechdel Test.",
            "scenes": scenes,
        }


def get_scene_content(script, scene_id):
    content = script.list_scenes[scene_id].list_lines
    if script.computed_score == 3:
        indexes_validating_lines = script.list_scenes[scene_id].validating_lines_score_3
        indexes_lines_male_words = {}
    elif script.computed_score == 2:
        indexes_validating_lines = script.list_scenes[scene_id].validating_lines_score_2
        indexes_lines_male_words = script.list_scenes[
            scene_id
        ].lines_with_male_words_score_2
    else:
        indexes_validating_lines = []
        indexes_lines_male_words = {}

    return {
        "scene_id": scene_id,
        "scene_content": content,
        "validating_lines": indexes_validating_lines,
        "lines_with_male_words": indexes_lines_male_words,
    }
