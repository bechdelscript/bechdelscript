from typing import List
import re

from script_parsing.naive_parsing import label, tag_script
from topic_modeling.import_masculine_words import import_masculine_words
from script_parsing.ml_parsing import tag_script_with_ml
from gender_name import classifier, _classify, gender_data
from pronouns.narrative_approach import import_gender_tokens
from pronouns.neural_coref import list_pronouns_coref
import nltk


class Script:
    def __init__(
        self, script_text: str, config: dict, ground_truth=None, user_genders=None
    ):
        self.script_text = script_text
        self.config = config
        self.user_genders = user_genders
        self.list_scenes: List[Scene] = []
        self.list_list_tags: List[List[label]] = []
        self.coherent_parsing: bool = None
        self.list_characters: List[Character] = []
        self.list_list_dialogues: List[List[Dialogue]] = []
        self.list_narration: All_Narration = []
        self.male_named_characters: List[Character] = []
        self.bechdel_ground_truth: int = ground_truth
        self.computed_score: int = 0
        self.score2_scenes: List[int] = []
        self.score3_scenes: List[int] = []
        self.bechdel_rules = self.config["bechdel_test_rules"]

    @classmethod
    def from_path(
        cls, script_path: str, config: dict, ground_truth=None, user_genders=None
    ):
        with open(script_path, "r") as f:
            script_text = f.read()
        return cls(script_text, config, ground_truth, user_genders)

    def load_format(self):
        self.load_scenes()
        self.identify_characters()
        self.check_parsing_is_coherent()
        self.reparse_if_incoherent()
        self.load_dialogues()
        self.load_narration()

    def bechdel(self):
        self.are_characters_named()
        self.identify_gender_named_chars()
        self.load_named_males()
        self.load_score_1()
        self.load_score_2()
        self.load_score_3()

    def load_scenes(self, with_ml: bool = False):
        if not with_ml:
            list_scenes, self.list_list_tags = tag_script(self.script_text)
        else:
            list_scenes, self.list_list_tags = tag_script_with_ml(
                self.config, self.script_text
            )
        self.list_scenes = []
        for i, scene in enumerate(list_scenes):
            self.list_scenes.append(Scene(scene, self.list_list_tags[i]))

    def identify_characters(self):
        self.list_characters = []
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

    def load_narration(self):
        narration = []
        for scene in self.list_scenes:
            scene.load_narration()
            narration += scene.list_narration
        self.list_narration = All_Narration(narration, self.config)

    def are_characters_named(self):
        for character in self.list_characters:
            character.fill_is_named(self.list_list_dialogues)

    def identify_gender_named_chars(self):
        para = self.config["used_methods"]["character_gender_method"]
        if para == "classify":
            function = lambda x: _classify(x, classifier)[0]
        elif para == "narrative":
            function = lambda x: self.list_narration.character_narrative_gender(x)
        elif para == "coref":
            pronouns = list_pronouns_coref(self.list_narration.list_contents)
            function = lambda x: self.list_narration.character_coref_gender(x, pronouns)
        for character in self.list_characters:
            if character.is_named:
                if self.user_genders and (character.name in self.user_genders.keys()):
                    character.gender = self.user_genders[character.name]
                else:
                    character.identify_gender(function)

    def load_named_males(self):
        for character in self.list_characters:
            if character.is_named:
                if character.gender == "m":
                    self.male_named_characters += [name.lower() for name in list(character.name_variation)]

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
                scene.is_elligible_characters_gender_method(
                    self.bechdel_rules["only_women_in_whole_scene"],
                    self.bechdel_rules["lines_of_dialogues_in_a_row"],
                )
                self.computed_score = min(
                    self.computed_score + scene.is_elligible_characters_gender, 2
                )
                if scene.is_elligible_characters_gender:
                    self.score2_scenes.append(index)
        # return score = 2 le cas échéant et liste de scènes qui valident le test 2

    def load_score_3(self):
        masculine_words = import_masculine_words(self.config)
        for index in self.score2_scenes:
            scene = self.list_scenes[index]
            scene.is_elligible_topic_method(
                self.male_named_characters,
                masculine_words,
                self.bechdel_rules["whole_discussion_not_about_men"],
                self.bechdel_rules["lines_of_dialogues_in_a_row"],
            )
            self.computed_score = min(self.computed_score + scene.is_elligible_topic, 3)
            if scene.is_elligible_topic:
                self.score3_scenes.append(index)
        # return score = 3 le cas échéant et liste de scènes qui valident le test 3

    def passes_bechdel_test(self):
        approved_scenes = self.score3_scenes
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

    def check_parsing_is_coherent(self):
        all_tags = sum(self.list_list_tags, [])
        self.coherent_parsing = True
        if (
            label.DIALOGUE not in all_tags
            or label.CHARACTER not in all_tags
            or label.SCENES_DESCRIPTION not in all_tags
            or label.SCENES_BOUNDARY not in all_tags
        ):
            self.coherent_parsing = False
        if len(self.list_characters) > 1000:
            self.coherent_parsing = False
        if len(self.list_scenes) == 1:
            self.coherent_parsing = False

    def reparse_if_incoherent(self):
        if not self.coherent_parsing and self.config["used_methods"]["reparse_with_ml"]:
            self.load_scenes(with_ml=True)
            self.identify_characters()
            self.check_parsing_is_coherent()


class Scene:
    def __init__(self, list_lines, list_tags):
        self.list_lines = list_lines
        self.list_tags = list_tags
        self.list_characters_in_scene = []
        self.list_dialogues = []
        self.list_narration = []
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

    def load_narration(self):
        current_narration = ""
        for i, line in enumerate(self.list_lines):
            if self.list_tags[i] == label.SCENES_DESCRIPTION:
                # new narrative passage
                current_narration += line.lstrip()

            elif self.list_tags[i] == label.METADATA:
                pass  # we simply ignore metadata

            elif self.list_tags[i] == label.SCENES_BOUNDARY:
                pass  # we simply ignore boundaries

            # if label is not narration nor metadata, then the ongoing narration is over
            else:
                if current_narration != "":
                    self.list_narration.append(current_narration)
                    current_narration = ""

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

    def is_elligible_characters_gender_method(
        self,
        only_women: bool,
        number_of_lines_in_a_row: int,
    ):
        if len(self.list_characters_in_scene) <= 1:
            return

        if only_women:
            self.is_elligible_characters_gender = self.are_characters_only_women()
        else:
            self.is_elligible_characters_gender = (
                self.are_characters_at_least_two_women(number_of_lines_in_a_row)
            )

    # Hard criteria : no men in scene at all
    def are_characters_only_women(self):
        is_elligible = True
        for character in self.list_characters_in_scene:
            if character.gender != "f":
                is_elligible = False
                break
        return is_elligible

    # Soft criteria :
    # Here, only two women in dialogue are sufficient to validate criteria 2,
    # as long as they exchange at least X lines (no matter which topic)
    def are_characters_at_least_two_women(self, number_of_lines_in_a_row):
        at_least_2_women = False
        female_count = 0
        for character in self.list_characters_in_scene:
            if character.gender == "f":
                female_count += 1
            if female_count >= 2:
                at_least_2_women = True
                break
        if not at_least_2_women:
            return False

        is_elligible = False
        characters_in_talking_order = [
            dialogue.character for dialogue in self.list_dialogues
        ]
        count_successive_false = 0
        last_person_talking = ""
        for character in characters_in_talking_order:
            #  A woman is talking, who is different that the last character speaking
            if character.gender == "f" and character.name != last_person_talking:
                count_successive_false += 1
            else:
                count_successive_false = 0
            last_person_talking = character.name
            # the number of successive feminine lines is reached
            if count_successive_false >= number_of_lines_in_a_row:
                is_elligible = True
                break
        return is_elligible

    def is_elligible_topic_method(
        self,
        males_names,
        masculine_words,
        whole_discussion: bool,
        number_of_lines_in_a_row: int,
    ):
        if self.list_dialogues == []:
            return

        if whole_discussion:
            self.is_elligible_topic = self.are_dialogues_about_men(
                males_names, masculine_words
            )
        else:
            self.is_elligible_topic = self.are_two_successive_lines_about_men(
                males_names, masculine_words, number_of_lines_in_a_row
            )

    # Hard criteria : no mentionning of men in all scene
    def are_dialogues_about_men(self, males_names, masculine_words):
        list_speak_about_men = [
            dialogue.speaks_about_men(masculine_words, males_names)
            for dialogue in self.list_dialogues
        ]
        if True in list_speak_about_men:
            is_elligible = False
        else:
            is_elligible = True
        return is_elligible

    # Soft Criteria :
    # Here, only two successive dialogue lines are sufficient to validate criteria 3 of the bechdel test
    def are_two_successive_lines_about_men(
        self,
        males_names,
        masculine_words,
        number_of_lines_in_a_row,
    ):
        list_speak_about_men = [
            (
                dialogue.speaks_about_men(masculine_words, males_names),
                dialogue.character,
            )
            for dialogue in self.list_dialogues
        ]
        is_elligible = False
        count_successive_false = 0
        last_person_talking = ""
        for about_men, character in list_speak_about_men:
            # about_men is False, said by a women, who is different that the last character talking
            if (
                not about_men
                and character.gender == "f"
                and character.name != last_person_talking
            ):
                count_successive_false += 1
            else:  # about_men is True, they're talking about men
                count_successive_false = 0
            last_person_talking = character.name
            # the number of successive feminine lines is reached
            if count_successive_false >= number_of_lines_in_a_row:
                is_elligible = True
                break
        return is_elligible

    def passes_bechdel_test(self):  ## fonction non utilisée
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
        self.clean_name()

    def clean_name(self):
        self.name = self.name.rstrip()
        # remove parenthesis after name
        parenthesis = re.search(r"\s*?\(.+\)", self.name)
        if parenthesis and parenthesis.span()[0] != 0:
            self.name = self.name[: parenthesis.span()[0]]

    def identify_gender(self, function):
        # _classify(self.name, classifier)[0]
        self.gender = function(self.name)

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
        speech: List[str],
    ):
        self.character = character
        self.speech_list = speech
        self.speech_text = " ".join(speech)
        self.clean_speech_text = self.clean_text()

    def speaks_about_men(self, masculine_words, males_names: List[str]):
        masculine_words = masculine_words + males_names
        words = self.clean_speech_text.split(" ")
        for word in words:
            if word in masculine_words:
                return True
        return False

    def clean_text(self):
        clean_speech_text = self.speech_text.strip()

        clean_speech_text = clean_speech_text.replace(".", " ")
        clean_speech_text = clean_speech_text.replace(",", " ")
        clean_speech_text = clean_speech_text.replace(";", " ")
        clean_speech_text = clean_speech_text.replace("?", " ")
        clean_speech_text = clean_speech_text.replace("!", " ")
        clean_speech_text = clean_speech_text.replace("(", " ")
        clean_speech_text = clean_speech_text.replace(")", " ")
        clean_speech_text = clean_speech_text.replace(":", " ")

        clean_speech_text = clean_speech_text.lower()

        return clean_speech_text

    def __repr__(self) -> str:
        return f"{self.character} : {self.speech_text}"


class All_Narration:
    def __init__(self, list_contents: List[str], config):
        self.list_contents = list_contents
        self.config = config
        self.tokens = import_gender_tokens(self.config)

    def character_narrative_gender(self, name: str):
        res = None
        if name.lower().split()[0] in gender_data["name"].values:
            temp = gender_data.loc[gender_data["name"] == name.lower().split()[0]][
                "gender"
            ].values[0]
            if temp != "f,m" and temp != "m,f":
                res = temp
        if res==None:
            # name = char.name
            freq_gender = {"m": 0, "f": 0, "nb": 0}
            paragraphs = [para for para in self.list_contents if name in para]
            for para in paragraphs:
                freq_tokens = dict.fromkeys(self.tokens[0], 0)
                freq = {}
                for word in nltk.word_tokenize(para):
                    for token in self.tokens[0]:
                        if token == word.lower():
                            freq_tokens[token] += 1
                for key in freq_tokens.keys():
                    gen = self.tokens.loc[self.tokens[0] == key][1].values[0]
                    value = freq_tokens[key]
                    try:
                        freq[gen] += value
                    except:
                        freq[gen] = value
                freq_gender[max(freq, key=lambda k: freq[k])] += 1
            res = max(freq_gender, key=lambda k: freq_gender[k])
        return res

    def character_coref_gender(self, name: str, pronouns):
        res = None
        if name.lower().split()[0] in gender_data["name"].values:
            temp = gender_data.loc[gender_data["name"] == name.lower().split()[0]][
                "gender"
            ].values[0]
            if (temp != "f,m") and (temp != "m,f"):
                res = temp
        if res == None:
            freq = {}
            clean_name = []
            for key in pronouns.keys():
                if name.lower() in str(key).lower():
                    clean_name.append(key)
            if clean_name != []:
                for clean in clean_name:
                    for key in pronouns[clean]:
                        if str(key).lower() in self.tokens[0].values:
                            gen = self.tokens.loc[self.tokens[0] == str(key).lower()][
                                1
                            ].values[0]
                            try:
                                freq[gen] += 1
                            except:
                                freq[gen] = 1
                if freq != {}:
                    res = max(freq, key=lambda k: freq[k])
        if res == None:
            res = self.character_narrative_gender(name)
        return res
