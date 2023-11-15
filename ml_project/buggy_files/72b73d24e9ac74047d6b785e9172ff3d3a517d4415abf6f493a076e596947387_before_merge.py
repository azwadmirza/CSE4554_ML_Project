def _lstrip_word(string, prefix):
    '''
    Return a copy of the string after the specified prefix was removed
    from the beginning of the string
    '''

    if string.startswith(prefix):
        return string[len(prefix):]
    return string