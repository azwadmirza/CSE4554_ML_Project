def _lstrip_word(word, prefix):
    '''
    Return a copy of the string after the specified prefix was removed
    from the beginning of the string
    '''

    if str(word).startswith(prefix):
        return str(word)[len(prefix):]
    return word