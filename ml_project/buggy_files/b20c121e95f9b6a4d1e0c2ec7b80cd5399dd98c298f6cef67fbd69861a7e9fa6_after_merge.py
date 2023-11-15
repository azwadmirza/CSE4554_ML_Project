def _unescape_str(text):
    """
    Unescapes a string according the TOML spec. Raises BadEscapeCharacter when appropriate.
    """
    text = text.decode('utf-8') if isinstance(text, six.binary_type) else text
    tokens = []
    i = 0
    basicstr_re = re.compile(r'[^"\\\000-\037]*')
    unicode_re = re.compile(r'[uU]((?<=u)[a-fA-F0-9]{4}|(?<=U)[a-fA-F0-9]{8})')
    escapes = {
        'b': '\b',
        't': '\t',
        'n': '\n',
        'f': '\f',
        'r': '\r',
        '\\': '\\',
        '"': '"',
        '/': '/',
        "'": "'"
    }
    while True:
        m = basicstr_re.match(text, i)
        i = m.end()
        tokens.append(m.group())
        if i == len(text) or text[i] != '\\':
            break
        else:
            i += 1
        if unicode_re.match(text, i):
            m = unicode_re.match(text, i)
            i = m.end()
            tokens.append(six.unichr(int(m.group(1), 16)))
        else:
            if text[i] not in escapes:
                raise BadEscapeCharacter
            tokens.append(escapes[text[i]])
            i += 1
    return ''.join(tokens)