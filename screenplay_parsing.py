import os
import re
from collections import Counter
from enum import Enum
from typing import Dict, List, Tuple

import numpy as np


class label(Enum):
    EMPTY_LINE = "E"
    SCENES_BOUNDARY_AND_DESCRIPTION = "SN"
    SCENES_BOUNDARY = "S"
    SCENES_DESCRIPTION = "N"
    CHARACTER = "C"
    SHORT_CAPITALIZED_TEXTS = "C?"
    DIALOGUE = "D"
    METADATA = "M"
    UNKNOWN = "?"


LABELS_PRIORITY = [
    label.CHARACTER,
    label.SCENES_BOUNDARY,
    label.METADATA,
    label.SCENES_BOUNDARY_AND_DESCRIPTION,
    label.DIALOGUE,
    label.SHORT_CAPITALIZED_TEXTS,
]

CHARACTER_KEYWORDS = [
    # looks for a capitalized letter (last letter of the name of the character speaking) followed
    # by (O.S.) eventually with a 0 instead of O and eventually with a space between the letters
    # must be at the end of a line (or followed only by whitespaces)
    r"[A-Z](\s)?\((O|0).\s?S.\)\s*(\n|$)",
    # same thing for (V.O)
    r"[A-Z](\s)?\(V\.\s?(O|0).\)\s*(\n|$)",
    # a capital letter followed by (CONT'D) or (CONT) or (CONTD)
    # must be at the end of a line (or followed only by whitespaces)
    r"[A-Z](\s)?\(CONT(\')?(D)?\)\s*(\n|$)",
]
BEGINNING_SCENES_KEYWORDS = [r"\bEXT\b", r"\bINT\b"]
ENDING_SCENES_KEYWORDS = [
    r"\bFADE IN\b",
    r"\bFADE OUT\b",
    r"\bFADE TO\b",
    r"\bFADE INTO\b",
    r"\bBACK TO\b",
    r"\bCUT TO\b",
    r"\bDISSOLVE TO\b",
]
META_KEYWORDS = [
    r"((^|\n)\s*\(+.*|.*\)($|\n))",  # looks for lines beginning or ending with parenthesis (or both)
]
DIALOGUE_KEYWORDS = [r"\?"]  # just question marks


def tag_script(script_path: str) -> Tuple[List[List[str]], List[label], bool]:
    """Assign a label to each line of a script.

    Args:
        script_path (str): path of the script

    Returns:
        Tuple[List[List[str]], List[label], bool ]: First element of the
            tuple is a list of scenes, each scene being a list of lines.
            The second element returned is the list of labels for each line.
            The last element indicates whether the parsing seems to have gone
            well or not.
    """
    with open(script_path) as f:
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
    coherent_parsing = check_parsing_is_coherent(characterized_indent_levels)

    tags = []
    for scene in scenes:
        tags.append(tag_lines(scene, characterized_indent_levels))

    return scenes, tags, coherent_parsing


def find_scenes(
    lines: List[str],
    beginning_scenes_keywords: List[str] = BEGINNING_SCENES_KEYWORDS,
    end_scenes_keywords: List[str] = ENDING_SCENES_KEYWORDS,
) -> List[List[str]]:
    """Splits the list of lines into sublists corresponding to the different scenes.
    The delimitation between the scenes is found thanks to specific keywords marking
    the beginning and the end of the keywords.

    Args:
        lines (List[str]): _description_
        beginning_scenes_keywords (List[str], optional): list of keywords usually found
            to mark the beginning of a scene. Defaults to BEGINNING_SCENES_KEYWORDS.
        end_scenes_keywords (List[str], optional): list of keywords usually found
            to mark the end of a scene. Defaults to ENDING_SCENES_KEYWORDS.

    Returns:
        List[List[str]]: List of scenes, each scene being a list of lines.
    """
    scenes = []
    current_scene = []
    for line in lines:
        has_keyword = False
        for keyword in beginning_scenes_keywords + end_scenes_keywords:
            if re.match(keyword, line):
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


def clean_scenes(scenes: List[List[str]]) -> List[List[str]]:
    """Scenes containing only empty lines are merged with the previous scene"""
    cleaned_scenes = []
    for scene in scenes:
        if len("".join(scene)) == 0 and len(cleaned_scenes) > 0:
            cleaned_scenes[-1] += scene
        else:
            cleaned_scenes.append(scene)
    return cleaned_scenes


def get_indents_list(lines: List[str]) -> List[int]:
    """Given a list of lines, returns a list of the number of white spaces
    that was before the text in each line. If the line is empty (i.e.
    it only contains white spaces), the number of white spaces is set to -1,
    this enables to differentiate the empty lines with the lines whose text
    is written without left white spaces.

    Args:
        lines (List[str]): list of lines from the script

    Returns:
        List[int]: list of the number of white spaces that was before
            the text in each line
    """
    indents = []
    for line in lines:
        len_line_with_no_left_spaces = len(line.lstrip())
        if len_line_with_no_left_spaces == 0:  # the line only had spaces
            indents.append(-1)
        else:
            indents.append(len(line) - len_line_with_no_left_spaces)
    return indents


def characterize_indent_levels(
    lines: List[str], indents: List[int], print_details: bool = False
) -> Dict[int, label]:
    """Given a script (or an extract of the script) as a list of lines, we try to
    identify for each level of indentation which label it should have. This method
    relies on the hypothesis that lines with the same indentation level all have
    the same label. The type of an indent level is identified using the number of
    keywords specific to a label as well as the frequency of capitalized letters
    and the mean length of words.

    Args:
        lines (List[str]): list of lines
        indents (List[int]): list of the number of white spaces found before
            the text in each line of lines

    Returns:
        Dict[int, label]: a dictionnary containing the label assigned to each
            indentation level (number of whitespaces being the keys)
    """

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
        indent_level = relevant_indent_levels[i]
        result[indent_level] = []
        if indent_level == -1:
            result[indent_level].append(label.EMPTY_LINE)
        else:
            if characters_keywords_occurences[i] > 0:
                result[indent_level].append(label.CHARACTER)
            if scenes_beginning_keywords_occurences[i] > 0:
                result[indent_level].append(label.SCENES_BOUNDARY_AND_DESCRIPTION)
            if scenes_ending_keywords_occurences[i] / len(group) > 0.8:
                result[indent_level].append(label.SCENES_BOUNDARY)
            if meta_keywords_occurences[i] / len(group) > 0.75:
                result[indent_level].append(label.METADATA)
            if (
                capitalized_frequency[i] > 0.9
                and mean_text_lengths[i] < 10
                and label.CHARACTER not in result[indent_level]
            ):
                result[indent_level].append(label.SHORT_CAPITALIZED_TEXTS)
            if dialogues_keywords_occurences[i] > 0:
                result[indent_level].append(label.DIALOGUE)
            if len(result[indent_level]) == 0:
                result[indent_level].append(label.UNKNOWN)

        while len(result[indent_level]) > 1:
            if LABELS_PRIORITY.index(result[indent_level][0]) > LABELS_PRIORITY.index(
                result[indent_level][1]
            ):
                result[indent_level].pop(0)
            else:
                result[indent_level].pop(1)

        result[indent_level] = result[indent_level][0]

        if result[indent_level] == label.SHORT_CAPITALIZED_TEXTS:
            if scenes_ending_keywords_occurences[i] > 1:
                result[indent_level] = label.SCENES_BOUNDARY
            else:
                result[indent_level] = label.CHARACTER

    if print_details:
        all_lists = {
            "In": relevant_indent_levels,
            "Re": [tag.value for tag in result.values()],
            "Le": mean_text_lengths,
            "Nb": [len(group) for group in groups],
            "Ca": capitalized_frequency,
            "Ch": characters_keywords_occurences,
            "SB": scenes_beginning_keywords_occurences,
            "SE": scenes_ending_keywords_occurences,
            "Me": meta_keywords_occurences,
            "Di": dialogues_keywords_occurences,
        }

        print_several_lists(list(all_lists.keys()), all_lists.values())

    return result


def group_lines_by_indent_level(
    lines: List[str], indents: List[int], minimum_occurences: int = 0
) -> List[List[str]]:
    """Splits a list of line into groups of lines such that each group
    contains all the lines that have the same level of indentation (i.e.
    the same number of left whitespaces)

    Args:
        lines (List[str]): list of lines from the script
        indents (List[int]): list of the number of left whitespaces for each line
        minimum_occurences (int, optional): groups that contain a number of line inferior
            to minimum occurences will be discarded, defaults to 0 (=never discard)

    Returns:
        List[List[str]]: groups containing all the lines with a given number
            of indentations
    """
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


def occurences_keywords_in_groups(
    groups: List[List[str]], keywords: List[str]
) -> List[int]:
    """Counts the number of keywords found in each group

    Args:
        groups (List[List[str]]): list of groups of lines, the lines within each group
            all have the same indent
        keywords (List[str]): list of keywords specific to a label

    Returns:
        List[int]: the number of keywords found in each group
    """
    groups_keyword_quantity = [0 for _ in range(len(groups))]
    for i, group in enumerate(groups):
        group_text = "\n".join(group)
        for keyword in keywords:
            groups_keyword_quantity[i] += len(re.findall(keyword, group_text))
    return groups_keyword_quantity


def frequency_capitalized_in_groups(groups: List[List[str]]) -> List[float]:
    """Computes the frequency of capitalized letter over the total number
    of letters for each group

    Args:
        groups (List[List[str]]): list of groups of lines, the lines within each group
            all have the same indent

    Returns:
        List[float]: the ratio of capitalized letters over the total number of
            letters, for each group
    """
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


def mean_text_length_in_groups(groups: List[List[str]]) -> List[float]:
    """Computes the mean lengths of the lines in each group (not counting the left
    whitespaces)

    Args:
        groups (List[List[str]]): list of groups of lines, the lines within each group
            all have the same indent

    Returns:
        List[float]: the mean length  for each group
    """
    groups_text_length = []
    for i, group in enumerate(groups):
        groups_text_length.append(
            round(sum([len(line.lstrip()) for line in group]) / len(group), 2)
        )
    return groups_text_length


def tag_lines(
    list_lines: List[str], characterized_indent_levels: Dict[int, label]
) -> List[label]:
    """Assign a label to each line in list_lines. In most cases the label
    assigned is the label corresponding to the label of its indentation level,
    except for the "SCENES_BOUNDARY_AND_DESCRIPTION" label where we look at the
    frequency of capitalized letters to decide whether the line is a scene
    boundary or a scene description. If the indent level of the line does not
    have a label, it is labelled as unknown.

    Args:
        list_lines (List[str]): list of lines
        characterized_indent_levels (Dict[int, label]): a dictionnary
            containing the label assigned to each indentation level

    Returns:
        List[label]: the list of labels for each line
    """
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


def check_parsing_is_coherent(characterized_indent_levels):
    if (
        label.DIALOGUE not in characterized_indent_levels.values()
        or label.CHARACTER not in characterized_indent_levels.values()
        or label.SCENES_BOUNDARY_AND_DESCRIPTION
        not in characterized_indent_levels.values()
    ):
        return False
    return True


### Functions below are only used to better visualize the parsing in order to improve it ###


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


def markdown_color_script(script_path, html=False):
    scenes, tags, coherent = tag_script(script_path)

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
