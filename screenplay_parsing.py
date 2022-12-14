import numpy as np
from collections import Counter
from enum import Enum


class label(Enum):
    EMPTY_LINE = "E"
    SCENES_BOUNDARY_AND_DESCRIPTION = "SN"
    SCENES_BOUNDARY = "S"
    SCENES_DESCRIPTION = "N"
    CHARACTER = "C"
    DIALOGUE = "D"
    METADATA = "M"
    UNKNOWN = "?"


CHARACTER_KEYWORDS = ["(O.S.)", "(CONT'D)", "(0.S.)", "(O. S.)", "(0. S.)", "(V.O.)"]
BEGINNING_SCENES_KEYWORDS = ["EXT ", "EXT.", "INT ", "INT."]
ENDING_SCENES_KEYWORDS = ["FADE IN", "FADE INTO", "CUT TO", "DISSOLVE TO"]
META_KEYWORDS = ["(", ")"]
DIALOGUE_KEYWORDS = ["?"]


def get_indents_list(lines):
    indents = []
    for line in lines:
        len_line_with_no_left_spaces = len(line.lstrip())
        if len_line_with_no_left_spaces == 0:  # the line only had spaces
            indents.append(-1)
        else:
            indents.append(len(line) - len_line_with_no_left_spaces)
    return indents


def find_scenes(
    lines,
    beginning_scenes_keywords=BEGINNING_SCENES_KEYWORDS,
    end_scenes_keywords=ENDING_SCENES_KEYWORDS,
):
    scenes = []
    current_scene = []
    for line in lines:
        has_keyword = False
        for keyword in beginning_scenes_keywords + end_scenes_keywords:
            if keyword in line:
                if keyword in beginning_scenes_keywords:
                    scenes.append(current_scene)
                    current_scene = [line]
                    has_keyword = True
                    break
                elif keyword in end_scenes_keywords:
                    current_scene.append(line)
                    scenes.append(current_scene)
                    current_scene = []
                    has_keyword = True
                    break
        if not has_keyword:
            current_scene.append(line)
    scenes.append(current_scene)
    return clean_scenes(scenes)


def clean_scenes(scenes):
    """Scenes containing only empty lines are merged with the previous scene"""
    cleaned_scenes = []
    for scene in scenes:
        if len("".join(scene)) == 0 and len(cleaned_scenes) > 0:
            cleaned_scenes[-1] += scene
        else:
            cleaned_scenes.append(scene)
    return cleaned_scenes


def occurences_keywords_in_groups(groups, keywords):
    groups_keyword_quantity = [0 for _ in range(len(groups))]
    for i, group in enumerate(groups):
        group_text = "".join(group)
        for keyword in keywords:
            groups_keyword_quantity[i] += group_text.count(keyword)
    return groups_keyword_quantity


def frequency_capitalized_in_groups(groups):
    groups_upper_quantity = [0 for _ in range(len(groups))]
    for i, group in enumerate(groups):
        group_text = "".join(group)
        total_letters = sum(
            (letter.isupper() or letter.islower()) for letter in group_text
        )
        if total_letters != 0:
            groups_upper_quantity[i] += round(
                sum(letter.isupper() for letter in group_text) / total_letters, 2
            )
        else:
            groups_upper_quantity[i] = 0
    return groups_upper_quantity


def mean_text_length_in_groups(groups):
    groups_text_length = []
    for i, group in enumerate(groups):
        groups_text_length.append(
            round(sum([len(line.lstrip()) for line in group]) / len(group), 2)
        )
    return groups_text_length


def print_several_lists(list_labels, lists):
    maximum_length = max(
        [max([len(str(element)) for element in sublist]) for sublist in lists]
    )
    for i, sublist in enumerate(lists):
        string = f"{list_labels[i]} : ["
        for element in sublist:
            string += " " * (maximum_length - len(str(element))) + str(element) + ", "
        string += "]"
        print(string)


def group_lines_by_indent_level(lines, indents, minimum_occurences=0):
    indents_counter = Counter(indents)
    relevant_indent_levels = []
    for indent_level in indents_counter:
        if indents_counter[indent_level] > minimum_occurences:
            relevant_indent_levels.append(indent_level)
    groups = []
    for indent_level in relevant_indent_levels:
        lines_idxs = np.where(np.array(indents) == indent_level)[0]
        group_lines = [lines[lines_idxs[i]] for i in range(len(lines_idxs))]
        groups.append(group_lines)
    return relevant_indent_levels, groups


def characterize_indent_levels(lines, indents):
    relevant_indent_levels, groups = group_lines_by_indent_level(
        lines, indents, minimum_occurences=0
    )
    mean_text_lengths = mean_text_length_in_groups(groups)
    capitalized_frequency = frequency_capitalized_in_groups(groups)
    characters_keywords_occurences = occurences_keywords_in_groups(
        groups, CHARACTER_KEYWORDS
    )
    scenes_beginning_keywords_occurences = occurences_keywords_in_groups(
        groups, BEGINNING_SCENES_KEYWORDS
    )
    scenes_ending_keywords_occurences = occurences_keywords_in_groups(
        groups, ENDING_SCENES_KEYWORDS
    )
    meta_keywords_occurences = occurences_keywords_in_groups(groups, META_KEYWORDS)
    dialogues_keywords_occurences = occurences_keywords_in_groups(
        groups, DIALOGUE_KEYWORDS
    )

    result = {}

    for i, group in enumerate(groups):
        if relevant_indent_levels[i] == -1:
            result[relevant_indent_levels[i]] = label.EMPTY_LINE
        elif characters_keywords_occurences[i] > 0:
            result[relevant_indent_levels[i]] = label.CHARACTER
        elif scenes_beginning_keywords_occurences[i] > 0:
            result[relevant_indent_levels[i]] = label.SCENES_BOUNDARY_AND_DESCRIPTION
        elif scenes_ending_keywords_occurences[i] / len(group) > 0.8:
            result[relevant_indent_levels[i]] = label.SCENES_BOUNDARY
        elif capitalized_frequency[i] > 0.9 and mean_text_lengths[i] < 10:
            result[relevant_indent_levels[i]] = label.CHARACTER
        elif meta_keywords_occurences[i] / len(group) > 1.0:
            # usually two parenthesis per line, one is the minimum
            result[relevant_indent_levels[i]] = label.METADATA
        elif dialogues_keywords_occurences[i] > 0:
            result[relevant_indent_levels[i]] = label.DIALOGUE
        else:
            result[relevant_indent_levels[i]] = label.UNKNOWN

    return result


def tag_lines(list_lines, characterized_indent_levels):
    indents = get_indents_list(list_lines)
    tags = []
    for i, line in enumerate(list_lines):
        if indents[i] in characterized_indent_levels:
            if (
                characterized_indent_levels[indents[i]]
                == label.SCENES_BOUNDARY_AND_DESCRIPTION
            ):
                if frequency_capitalized_in_groups([line])[0] > 0.8:
                    tags.append(label.SCENES_BOUNDARY)
                else:
                    tags.append(label.SCENES_DESCRIPTION)
            else:
                tags.append(characterized_indent_levels[indents[i]])
        else:
            tags.append(label.UNKNOWN)

    return tags


def tag_script(script_path):
    with open(script_path, errors="ignore") as f:
        screenplay = f.read()

    lines = screenplay.split("\n")
    scenes = find_scenes(lines)

    indents = get_indents_list(lines)
    # We remove the first and last scenes (which often contain the title of
    # the movie etc.), then we assign a label to each indent level
    if len(scenes) > 2:
        middle_indents = indents[len(scenes[0]) : -len(scenes[-1])]
        middle_lines = sum(scenes[1:-1], [])
    else:
        middle_indents = indents
        middle_lines = lines

    characterized_indent_levels = characterize_indent_levels(
        middle_lines, middle_indents
    )
    tags = []
    for scene in scenes:
        tags.append(tag_lines(scene, characterized_indent_levels))

    return scenes, tags


import os


def markdown_color_script(script_path, html=False):
    scenes, tags = tag_script(script_path)

    movie_name = os.path.split(script_path)[1].split(".")[0] + (
        ".html" if html else ".md"
    )
    with open(
        os.path.join("data", "intermediate", "colored_scripts", movie_name), "w+"
    ) as f:
        for scene_idx, scene in enumerate(scenes):
            for line_idx, line in enumerate(scene):
                write_one_markdown_line(f, line, tags[scene_idx][line_idx])
            if not html:
                f.write("\n")
                f.write("---\n")
                f.write("\n")


def write_one_markdown_line(f, line, tag):
    color_correspondance = {
        label.EMPTY_LINE: "rosybrown",
        label.SCENES_BOUNDARY: "dodgerblue",
        label.SCENES_DESCRIPTION: "hotpink",
        label.CHARACTER: "gold",
        label.DIALOGUE: "peru",
        label.METADATA: "olivedrab",
        label.UNKNOWN: "snow",
    }
    line = f"{tag.value}    {line}"
    line = line.replace(" ", "&nbsp;")
    line = line.replace("	", "&nbsp;" * 4)
    f.write(f'<span style="color:{color_correspondance[tag]}">{line}</span><br>\n')


if __name__ == "__main__":
    from random import choice

    folder_name = "data/input/scripts_imsdb"
    script_name = choice(os.listdir(folder_name))
    print(script_name)
    # markdown_color_script(os.path.join(folder_name, script_name))
    print(tag_script(os.path.join(folder_name, script_name))[0][:2])
