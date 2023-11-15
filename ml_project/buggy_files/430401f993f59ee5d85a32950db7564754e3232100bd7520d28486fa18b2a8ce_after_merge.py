def is_binary(data):
    '''
    Detects if the passed string of data is binary or text
    '''
    if not data or not isinstance(data, (six.string_types, six.binary_type)):
        return False

    if isinstance(data, six.binary_type):
        if b'\0' in data:
            return True
    elif str('\0') in data:
        return True

    text_characters = ''.join([chr(x) for x in range(32, 127)] + list('\n\r\t\b'))
    # Get the non-text characters (map each character to itself then use the
    # 'remove' option to get rid of the text characters.)
    if six.PY3:
        if isinstance(data, six.binary_type):
            import salt.utils.data
            nontext = data.translate(None, salt.utils.data.encode(text_characters))
        else:
            trans = ''.maketrans('', '', text_characters)
            nontext = data.translate(trans)
    else:
        if isinstance(data, six.text_type):
            trans_args = ({ord(x): None for x in text_characters},)
        else:
            trans_args = (None, str(text_characters))  # future lint: blacklisted-function
        nontext = data.translate(*trans_args)

    # If more than 30% non-text characters, then
    # this is considered binary data
    if float(len(nontext)) / len(data) > 0.30:
        return True
    return False