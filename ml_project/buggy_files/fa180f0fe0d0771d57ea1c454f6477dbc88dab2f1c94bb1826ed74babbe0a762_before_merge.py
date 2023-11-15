def is_lyrics(text, artist=None):
    """Determine whether the text seems to be valid lyrics.
    """
    if not text:
        return
    badTriggersOcc = []
    nbLines = text.count('\n')
    if nbLines <= 1:
        log.debug(u"Ignoring too short lyrics '{0}'".format(
                  text.decode('utf8')))
        return 0
    elif nbLines < 5:
        badTriggersOcc.append('too_short')
    else:
        # Lyrics look legit, remove credits to avoid being penalized further
        # down
        text = remove_credits(text)

    badTriggers = ['lyrics', 'copyright', 'property', 'links']
    if artist:
        badTriggersOcc += [artist]

    for item in badTriggers:
        badTriggersOcc += [item] * len(re.findall(r'\W%s\W' % item,
                                                  text, re.I))

    if badTriggersOcc:
        log.debug(u'Bad triggers detected: {0}'.format(badTriggersOcc))

    return len(badTriggersOcc) < 2