from screenplay_parsing import tag_script, label
from typing import List


class Script:
    def __init__(
        self,
        script_path,
    ):
        self.script_path = script_path
        self.list_scenes: List[Scene] = []
        self.list_list_tags: List[List[label]] = []
        self.list_characters: List[Characters] = []

        self.load_scenes()
        self.identify_characters()

    def load_scenes(self):
        list_scenes, self.list_list_tags = tag_script(self.script_path)
        for i, scene in enumerate(list_scenes):
            self.list_scenes.append(Scene(scene, self.list_list_tags[i]))

    def identify_characters(self):
        list_scenes, self.list_list_tags = tag_script(self.script_path)
        for i, scene in enumerate(list_scenes):
            for j, lab in enumerate(self.list_list_tags[i]):
                if lab == label.CHARACTER:
                    name = scene[j].lstrip()
                    already_in = False
                    for name_og in self.list_characters:
                        if name_og.name.startswith(name) or name.startswith(name_og.name):
                            name_og.add_name_variation(name)
                            break
                    if already_in == False:
                        self.list_characters.append(Characters(scene[j].lstrip()))
        self.list_characters = list(dict.fromkeys(self.list_characters))



class Scene:
    def __init__(self, list_lines, list_tags):
        self.list_lines = list_lines
        self.list_tags = list_tags
        self.list_characters = []
        self.list_dialogues = []


class Characters:
    def __init__(self, name, gender=None, is_named=None):
        self.name = name
        self.name_variation = {name}
        self.gender = gender
        self.is_named = is_named

    def identify_gender(self):
        NotImplemented

    def get_is_named(self):
        NotImplemented
    
    def add_name_variation(self, other):
        self.name_variation.add(other)


class Dialogue:
    def __init__(self, character, metadata, speech):
        self.character = character
        self.metadata = metadata
        self.speech = speech

    def speak_of_men(self):
        NotImplemented


if __name__ == "__main__":

    from random import choice
    import os

    folder_name = "data/input/scripts_imsdb"
    script_name = choice(os.listdir(folder_name))

    script = Script(os.path.join(folder_name, script_name))

    print(script.list_characters[3].name, script.list_characters[3].name_variation)
