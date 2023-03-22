def clean_text(string, strip=True, add_spaces_to_extremities=False):
    if strip:
        string = string.strip()

    if add_spaces_to_extremities:
        string = " " + string + " "

    clean_string = string.replace(".", " ")
    clean_string = clean_string.replace(",", " ")
    clean_string = clean_string.replace(";", " ")
    clean_string = clean_string.replace("?", " ")
    clean_string = clean_string.replace("!", " ")
    clean_string = clean_string.replace("(", " ")
    clean_string = clean_string.replace(")", " ")
    clean_string = clean_string.replace(":", " ")
    clean_string = clean_string.replace("'", " ")

    clean_string = clean_string.lower()

    return clean_string
