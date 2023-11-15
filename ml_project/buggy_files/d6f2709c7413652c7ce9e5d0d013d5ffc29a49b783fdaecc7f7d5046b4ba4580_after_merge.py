def canonical_name(obj, fmt=u'{key}:{value}', separator=u'|', ignore_list=frozenset()):
    """Create a canonical name from a release name or a guessed dictionary.

    The return value is always unicode.

    :param obj:
    :type obj: str or dict
    :param fmt:
    :type fmt: str or unicode
    :param separator:
    :type separator: str or unicode
    :param ignore_list:
    :type ignore_list: set
    :return:
    :rtype: text_type
    """
    guess = obj if isinstance(obj, dict) else guessit.guessit(obj)
    return text_type(
        text_type(separator).join(
            [text_type(fmt).format(key=unicodify(k), value=unicodify(v))
             for k, v in guess.items() if k not in ignore_list]))