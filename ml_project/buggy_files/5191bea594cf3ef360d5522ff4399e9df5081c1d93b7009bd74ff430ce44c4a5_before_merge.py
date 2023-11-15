def preprocessing(txt: str, remove_space: bool = True) -> str:
    """
    Clean up text before performing evaluation

    :param str text: text to be preprocessed
    :param bool remove_space: whether remove white space

    :return: preprocessed text
    :rtype: str
    """
    txt = re.sub(SURROUNDING_SEPS_RX, "", txt)

    if remove_space:
        txt = re.sub("\s+", "", txt)

    txt = re.sub(
        MULTIPLE_SEPS_RX,
        SEPARATOR,
        txt
    )

    txt = re.sub(TAG_RX, "", txt)

    txt = re.sub(TAILING_SEP_RX, "", txt).strip()

    return txt