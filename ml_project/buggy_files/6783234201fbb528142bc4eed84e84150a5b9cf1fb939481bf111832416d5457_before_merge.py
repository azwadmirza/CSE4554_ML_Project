def _onPygletKey(symbol, modifiers, emulated=False):
    """handler for on_key_press pyglet events; call directly to emulate a
    key press

    Appends a tuple with (keyname, timepressed) into the global _keyBuffer.
    The _keyBuffer can then be accessed as normal using event.getKeys(),
    .waitKeys(), clearBuffer(), etc.

    J Gray 2012: Emulated means add a key (symbol) to the buffer virtually.
    This is useful for fMRI_launchScan, and for unit testing (in testTheApp)
    Logging distinguishes EmulatedKey events from real Keypress events.
    For emulation, the key added to the buffer is unicode(symbol), instead of
    pyglet.window.key.symbol_string(symbol).

    S Mathot 2012: Implement fallback to _onPygletText

    5AM Solutions 2016: Add the keyboard modifier flags to the key buffer.

    M Cutone 2018: Added GLFW backend support.

    """
    global useText

    keyTime = psychopy.core.getTime()  # capture when the key was pressed
    if emulated:
        if not isinstance(modifiers, int):
            msg = 'Modifiers must be passed as an integer value.'
            raise ValueError(msg)

        thisKey = str(symbol)
        keySource = 'EmulatedKey'
    else:
        thisKey = pyglet.window.key.symbol_string(
            symbol).lower()  # convert symbol into key string
        # convert pyglet symbols to pygame forms ( '_1'='1', 'NUM_1'='[1]')
        # 'user_key' indicates that Pyglet has been unable to make sense
        # out of the keypress. In that case, we fall back to _onPygletText
        # to handle the input.
        if 'user_key' in thisKey:
            useText = True
            return
        useText = False
        thisKey = thisKey.lstrip('_').lstrip('NUM_')
        # Pyglet 1.3.0 returns 'enter' when Return key (0xFF0D) is pressed 
        # in Windows Python3. So we have to replace 'enter' with 'return'.
        if thisKey == 'enter':
            thisKey = 'return'
        keySource = 'Keypress'
    _keyBuffer.append((thisKey, modifiers, keyTime))  # tuple
    logging.data("%s: %s" % (keySource, thisKey))
    _process_global_event_key(thisKey, modifiers)