def guess_format(filename: Text) -> Text:
    """Applies heuristics to guess the data format of a file.

    Args:
        filename: file whose type should be guessed

    Returns:
        Guessed file format.
    """
    guess = UNK
    content = rasa.utils.io.read_file(filename)
    try:
        js = json.loads(content)
    except ValueError:
        if any([marker in content for marker in _markdown_section_markers]):
            guess = MARKDOWN
    else:
        for fformat, format_heuristic in _json_format_heuristics.items():
            if format_heuristic(js, filename):
                guess = fformat
                break

    return guess