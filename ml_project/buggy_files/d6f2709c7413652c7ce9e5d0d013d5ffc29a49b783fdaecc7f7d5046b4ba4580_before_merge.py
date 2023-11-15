def canonical_name(obj, fmt='{key}:{value}', separator='|', ignore_list=frozenset()):
    """Create a canonical name from a release name or a guessed dictionary.

    :param obj:
    :type obj: str or dict
    :param fmt:
    :type fmt: str or unicode
    :param separator:
    :type separator: str or unicode
    :param ignore_list:
    :type ignore_list: set
    :return:
    :rtype: str
    """
    guess = obj if isinstance(obj, dict) else guessit.guessit(obj)
    return str(separator.join([fmt.format(key=k, value=v) for k, v in guess.items() if k not in ignore_list]))