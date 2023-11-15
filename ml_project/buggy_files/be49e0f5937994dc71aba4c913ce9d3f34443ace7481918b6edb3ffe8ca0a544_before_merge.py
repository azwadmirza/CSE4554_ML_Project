def clean_value(name):
    # Move anything in leading brackets to the end
    # name = re.sub(r'^\[(.*?)\](.*)', r'\2 \1', name)

    for char in '[]()_,.':
        name = name.replace(char, ' ')

    # if there are no spaces
    if name.find(' ') == -1:
        name = name.replace('-', ' ')

    # remove unwanted words (imax, ..)
    # self.remove_words(data, self.remove)

    # MovieParser.strip_spaces
    name = ' '.join(name.split())
    return name