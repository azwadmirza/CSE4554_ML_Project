def is_binary(data):
    '''
    Detects if the passed string of data is binary or text
    '''
    if not data or not isinstance(data, six.string_types):
        return False
    if '\0' in data:
        return True

    text_characters = ''.join([chr(x) for x in range(32, 127)] + list('\n\r\t\b'))
    # Get the non-text characters (map each character to itself then use the
    # 'remove' option to get rid of the text characters.)
    if six.PY3:
        trans = ''.maketrans('', '', text_characters)
        nontext = data.translate(trans)
    else:
        if isinstance(data, unicode):  # pylint: disable=incompatible-py3-code
            trans_args = ({ord(x): None for x in text_characters},)
        else:
            trans_args = (None, str(text_characters))  # future lint: blacklisted-function
        nontext = data.translate(*trans_args)

    # If more than 30% non-text characters, then
    # this is considered binary data
    if float(len(nontext)) / len(data) > 0.30:
        return True
    return False