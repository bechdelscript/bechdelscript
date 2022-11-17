from typing import List

from screenplay_parsing import label, tag_script


class Script:
    def __init__(
        self,
        script_path,
    ):
        self.script_path = script_path
        self.list_scenes: List[Scene] = []
        self.list_list_tags: List[List[label]] = []
        self.list_characters = []
        self.list_list_dialogues = []

        self.load_scenes()
        self.identify_characters()
        self.load_dialogues()
        self.are_characters_named()

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
                        if name_og.name.startswith(name) or name.startswith(
                            name_og.name
                        ):
                            name_og.add_name_variation(name)
                            already_in = True
                            break
                    if already_in == False:
                        self.list_characters.append(Characters(scene[j].lstrip()))

    def load_dialogues(self):
        for scene in self.list_scenes:
            scene.load_dialogues(self.list_characters)
            self.list_list_dialogues.append(scene.list_dialogues)

    def are_characters_named(self):
        for character in self.list_characters:
            character.fill_is_named(self.list_list_dialogues)


class Scene:
    def __init__(self, list_lines, list_tags):
        self.list_lines = list_lines
        self.list_tags = list_tags
        self.list_characters_in_scene = []
        self.list_dialogues = []

    def load_dialogues(self, characters_in_movie):
        current_speech = []
        current_speaker = None
        for i, line in enumerate(self.list_lines):
            if self.list_tags[i] == label.DIALOGUE:
                # new dialogue, we have to find who is speaking
                if current_speech == []:
                    current_speaker = self.find_speaker(i, characters_in_movie)
                    current_speech.append(line.lstrip())
                else:
                    current_speech.append(line.lstrip())

            elif self.list_tags[i] == label.METADATA:
                pass  # we simply ignore metadata

            # if label is not dialogue nor metadata, then the ongoing dialogue is over
            else:
                if current_speech != []:
                    # If we weren't able to identify speaker, then it's
                    # likely because the line is not a real dialogue
                    if current_speaker != None:
                        self.list_dialogues.append(
                            Dialogue(current_speaker, current_speech)
                        )
                    current_speaker = None
                    current_speech = []

    def find_speaker(self, dialogue_beginning_index: int, characters_in_movie: List):
        """Searches a line tagged character before the dialogue beginning index, and
        matches this line to the corresponding character among the characters of the movie

        Args:
            dialogue_beginning_index (int): index of the beginning of the dialogue whose speaker
                we are trying to identify
            characters_in_movie (List[Characters]): list of characters in the movie

        Returns:
            Union[Characters, None]: The speaker of the dialogue, if found, else None
        """
        # We check the line above, if it's a character name, then it is the speaker
        search_index = dialogue_beginning_index - 1
        while search_index > 0 and self.list_tags[search_index] in [
            label.CHARACTER,
            label.METADATA,
        ]:
            if self.list_tags[search_index] == label.CHARACTER:
                speaker_name = self.list_lines[search_index].lstrip()
                # in theory, each name variation should correspond to only one character
                current_speaker = [
                    character
                    for character in characters_in_movie
                    if speaker_name in character.name_variation
                ][0]
                return current_speaker
            search_index -= 1
        return None


class Characters:
    def __init__(self, name, gender=None, is_named=None):
        self.name = name
        self.name_variation = {name}
        self.gender = gender
        self.is_named = is_named

    def identify_gender(self):
        NotImplemented

    def add_name_variation(self, other):
        self.name_variation.add(other)

    def fill_is_named(self, list_list_dialogues):
        self.is_named = False
        # transform dialogues of all movie in one string
        concatenated_dialogues = " ".join(
            [
                " ".join([dialogue.speech_text for dialogue in scene])
                for scene in list_list_dialogues
            ]
        )
        for name_variation in self.name_variation:
            if name_variation.capitalize() in concatenated_dialogues:
                self.is_named = True

    def __repr__(self) -> str:
        return self.name


class Dialogue:
    def __init__(self, character: Characters, speech: List[str]):
        self.character = character
        self.speech_list = speech
        self.speech_text = " ".join(speech)

    def speak_of_men(self):
        NotImplemented

    def __repr__(self) -> str:
        return f"{self.character} : {self.speech_text}"


if __name__ == "__main__":

    import os
    from random import choice

    folder_name = "data/input/scripts_imsdb"
    script_name = choice(os.listdir(folder_name))

    script = Script(os.path.join(folder_name, script_name))

    print(script.list_characters[3].name, script.list_characters[3].name_variation)
