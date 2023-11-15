def _onPygletText(text, emulated=False):
    """handler for on_text pyglet events, or call directly to emulate a text
    event.

    S Mathot 2012: This function only acts when the key that is pressed
    corresponds to a non-ASCII text character (Greek, Arabic, Hebrew, etc.).
    In that case the symbol that is passed to _onPygletKey() is translated
    into a useless 'user_key()' string. If this happens, _onPygletText takes
    over the role of capturing the key. Unfortunately, _onPygletText()
    cannot solely handle all input, because it does not respond to spacebar
    presses, etc.
    """

    global useText
    if not useText:  # _onPygletKey has handled the input
        return
    # This is needed because sometimes the execution
    # sequence is messed up (somehow)
    useText = False
    # capture when the key was pressed:
    keyTime = psychopy.core.getTime()
    if emulated:
        keySource = 'EmulatedKey'
    else:
        keySource = 'KeyPress'
    _keyBuffer.append((text.lower(), lastModifiers, keyTime))
    logging.data("%s: %s" % (keySource, text))