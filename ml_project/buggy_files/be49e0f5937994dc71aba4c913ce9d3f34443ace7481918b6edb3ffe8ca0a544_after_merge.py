def clean_value(name):
    for char in '[]()_,.':
        name = name.replace(char, ' ')

    # if there are no spaces
    if name.find(' ') == -1:
        name = name.replace('-', ' ')

    # MovieParser.strip_spaces
    name = ' '.join(name.split())
    return name