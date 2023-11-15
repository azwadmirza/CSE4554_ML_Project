def get_words(text, exclude_offset=None, language=None):
    """
    Extract all words from a source code file to be used in code completion.

    Extract the list of words that contains the file in the editor,
    to carry out the inline completion similar to VSCode.
    """
    regex = LANGUAGE_REGEX.get(language.lower(), all_regex)
    tokens = [x
              for x in (m.group()
                        for m in regex.finditer(text)
                        if exclude_offset is None or
                        exclude_offset < m.start() or
                        m.end() < exclude_offset)
              if x != '']
    return tokens