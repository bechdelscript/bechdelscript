from typing import List

from screenplay_parsing import label, tag_script
from topic_modeling.naive_approach import import_masculine_words
from gender_name import classifier, _classify, classify


class Script:
    def __init__(self, script_path, ground_truth=None):
        self.script_path = script_path
        self.list_scenes: List[Scene] = []
        self.list_list_tags: List[List[label]] = []
        self.coherent_parsing: bool = None
        self.list_characters: List[Character] = []
        self.list_list_dialogues: List[List[Dialogue]] = []
        self.male_named_characters: List[Character] = []
        self.bechdel_ground_truth: int = ground_truth
        self.computed_score: int = 0
        self.score2_scenes: List[int] = []
        self.score3_scenes: List[int] = []

        self.load_scenes()
        self.identify_characters()
        self.load_dialogues()
        self.are_characters_named()
        self.identify_gender_named_chars()
        self.load_named_males()
        self.load_score_1()
        self.load_score_2()
        self.load_score_3()

    def load_scenes(self):
        list_scenes, self.list_list_tags, self.coherent_parsing = tag_script(
            self.script_path
        )
        for i, scene in enumerate(list_scenes):
            self.list_scenes.append(Scene(scene, self.list_list_tags[i]))

    def identify_characters(self):
        for i, scene in enumerate(self.list_scenes):
            for j, lab in enumerate(self.list_list_tags[i]):
                if lab == label.CHARACTER:
                    name = scene.list_lines[j].lstrip()
                    already_in = False
                    char_if_already_in = None
                    for name_og in self.list_characters:
                        if name_og.name.startswith(name) or name.startswith(
                            name_og.name
                        ):
                            name_og.add_name_variation(name)
                            already_in = True
                            char_if_already_in = name_og
                            break
                    if already_in == False:
                        new_character = Character(scene.list_lines[j].lstrip())
                        self.list_characters.append(new_character)
                        scene.list_characters_in_scene.append(new_character)
                    else:
                        if char_if_already_in not in scene.list_characters_in_scene:
                            scene.list_characters_in_scene.append(char_if_already_in)

    def load_dialogues(self):
        for scene in self.list_scenes:
            scene.load_dialogues(self.list_characters)
            self.list_list_dialogues.append(scene.list_dialogues)

    def are_characters_named(self):
        for character in self.list_characters:
            character.fill_is_named(self.list_list_dialogues)

    def identify_gender_named_chars(self):
        for character in self.list_characters:
            if character.is_named == True:
                character.identify_gender()

    def load_named_males(self):
        for character in self.list_characters:
            if character.is_named == True:
                if character.gender == "m":
                    self.male_named_characters += list(character.name_variation)

    def load_score_1(self):
        females = [
            character
            for character in self.list_characters
            if character.is_named == True and character.gender == "f"
        ]
        self.computed_score += len(females) >= 2

    def load_score_2(self):
        if self.computed_score == 1:
            for index, scene in enumerate(self.list_scenes):
                scene.are_characters_only_women()
                self.computed_score = min(
                    self.computed_score + scene.is_elligible_characters_gender, 2
                )
                if scene.is_elligible_characters_gender:
                    self.score2_scenes.append(index)
        # return score = 2 le cas échéant et liste de scènes qui valident le test 2

    def load_score_3(self):
        masculine_words = import_masculine_words()
        for index in self.score2_scenes:
            scene = self.list_scenes[index]
            scene.are_dialogues_about_men(self.male_named_characters, masculine_words)
            self.computed_score = min(self.computed_score + scene.is_elligible_topic, 3)
            if scene.is_elligible_topic:
                self.score3_scenes.append(index)
        # return score = 3 le cas échéant et liste de scènes qui valident le test 3

    def passes_bechdel_test(self):
        bechdel_approved = False
        approved_scenes = self.score3_scenes
        if self.computed_score == 3:
            bechdel_approved = True

        script_bechdel_approved = len(approved_scenes) >= 1

        return script_bechdel_approved, approved_scenes

    def display_results(self, nb_scenes):
        print(f"Computed score : {self.computed_score}")
        if self.computed_score == 0:
            print("There aren't two named women in the movie.")
            print("List of named characters in the movie :")
            for character in self.list_characters:
                if character.is_named:
                    print(f"- {character.name} ({character.gender})")
        elif self.computed_score >= 1:
            named_women_characters = [
                character.name
                for character in self.list_characters
                if character.is_named and character.gender == "f"
            ]
            print(
                f"""There is at least two women who are named : {
                    ", ".join(named_women_characters)
                }\n"""
            )
            if self.computed_score == 1:
                print(
                    "However, they never talk in the same scene without other men, here are some scenes where they appear :"
                )
                current_nb_scenes = 0
                for i, scene in enumerate(self.list_scenes):
                    for named_woman in named_women_characters:
                        if (
                            any(
                                [
                                    named_woman.startswith(character.name)
                                    or character.name.startswith(named_woman)
                                    for character in scene.list_characters_in_scene
                                ]
                            )
                            > 0
                        ):
                            print(
                                f"""- Scene number {i} with characters : {
                                    ", ".join(
                                        [
                                            f"{character.name} ({character.gender})"
                                            for character in scene.list_characters_in_scene
                                        ]
                                    )
                                }"""
                            )
                            current_nb_scenes += 1
                    if current_nb_scenes == 5:
                        break
            else:
                if self.computed_score == 2:
                    relevant_scenes = self.score2_scenes
                    print(
                        f"And they talk with each other in {len(self.score2_scenes)} scenes, here are some of them :"
                    )
                    for i in self.score2_scenes[:5]:
                        print(
                            f"""- Scene number {i} with characters : {
                                ", ".join(
                                    [
                                        f"{character.name} ({character.gender})"
                                        for character in self.list_scenes[i].list_characters_in_scene
                                    ]
                                )
                            }"""
                        )
                    print("However, they talk about men in all of those scenes.")

                elif self.computed_score == 3:
                    relevant_scenes = self.score3_scenes
                    print(
                        f"And they talk with each other about things other than men in {len(self.score3_scenes)} scenes, here are some of them :"
                    )
                    for i in self.score3_scenes[:5]:
                        print(
                            f"""- Scene number {i} with characters : {
                                ", ".join(
                                    [
                                        f"{character.name} ({character.gender})"
                                        for character in self.list_scenes[i].list_characters_in_scene
                                    ]
                                )
                            }"""
                        )
                nb_scenes_to_print = min(nb_scenes, len(relevant_scenes))
                print(
                    f"\nHere {'are' if nb_scenes_to_print > 1 else 'is'} {nb_scenes_to_print} {'scenes' if nb_scenes_to_print > 1 else 'scene'} that validate this score :"
                )
                for scene_id in relevant_scenes[:nb_scenes_to_print]:
                    print(
                        f"\n******* {str(scene_id) + 'th' if scene_id == 1 else str(scene_id) + 'st'} scene *******"
                    )
                    print(self.list_scenes[scene_id])


class Scene:
    def __init__(self, list_lines, list_tags):
        self.list_lines = list_lines
        self.list_tags = list_tags
        self.list_characters_in_scene = []
        self.list_dialogues = []
        self.is_elligible_characters_gender = False
        self.is_elligible_topic = False

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
            characters_in_movie (List[Character]): list of characters in the movie

        Returns:
            Union[Character, None]: The speaker of the dialogue, if found, else None
        """
        # We check the line above, if it's a character name, then it is the speaker
        search_index = dialogue_beginning_index - 1
        while search_index > 0 and self.list_tags[search_index] in [
            label.CHARACTER,
            label.METADATA,
            label.EMPTY_LINE,
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

    def are_characters_only_women(self):
        if len(self.list_characters_in_scene) <= 1:
            return

        is_elligible = True
        for character in self.list_characters_in_scene:
            if character.gender != "f":
                is_elligible = False
                break
        self.is_elligible_characters_gender = is_elligible

    def are_dialogues_about_men(self, males_names, masculine_words):
        if self.list_dialogues == []:
            return

        list_speak_about_men = [
            dialogue.speaks_about_men(masculine_words, males_names)
            for dialogue in self.list_dialogues
        ]
        if True in list_speak_about_men:
            is_elligible = False
        else:
            is_elligible = True
        self.is_elligible_topic = is_elligible

    def passes_bechdel_test(self):
        passes_bechdel = True
        if not self.is_elligible_characters_gender:
            passes_bechdel = False
        if not self.is_elligible_topic:
            passes_bechdel = False
        return passes_bechdel

    def __repr__(self) -> str:
        return "\n".join(self.list_lines)


class Character:
    def __init__(self, name, gender=None, is_named=None):
        self.name = name
        self.name_variation = {name}
        self.gender = gender
        self.is_named = is_named

    def identify_gender(self):
        self.gender = _classify(self.name, classifier)[0]

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
    def __init__(
        self,
        character: Character,
        speech: List[str],  # movie_characters: List[Character]
    ):
        self.character = character
        self.speech_list = speech
        self.speech_text = " ".join(speech)
        self.clean_speech_text = self.clean_text()

    def speaks_about_men(self, males_names: List[str], masculine_words):
        masculine_words = masculine_words + males_names
        words = self.clean_speech_text.split(" ")
        for word in words:
            if word in masculine_words:
                return True
        return False

    def clean_text(self):

        clean_speech_text = self.speech_text.replace(".", "")
        clean_speech_text = clean_speech_text.replace(",", "")
        clean_speech_text = clean_speech_text.replace(";", "")
        clean_speech_text = clean_speech_text.replace("?", "")
        clean_speech_text = clean_speech_text.replace("!", "")
        clean_speech_text = clean_speech_text.replace("(", "")
        clean_speech_text = clean_speech_text.replace(")", "")
        clean_speech_text = clean_speech_text.replace(":", "")

        clean_speech_text = clean_speech_text.casefold()

        return clean_speech_text

    def __repr__(self) -> str:
        return f"{self.character} : {self.speech_text}"
