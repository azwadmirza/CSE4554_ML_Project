def _escape_single_line_quoted_string(text):
    text = text.decode('utf-8') if isinstance(text, six.binary_type) else text
    start = 0
    i = 0
    res = []
    _escapes = {'\n': '\\n', '\r': '\\r', '\\': '\\\\', '\t': '\\t',
                '\b': '\\b', '\f': '\\f', '"': '\\"'}

    def flush():
        if start < i:
            res.append(text[start:i])
        return i + 1

    while i < len(text):
        c = text[i]
        if c in _escapes:
            start = flush()
            res.append(_escapes[c])
        elif ord(c) < 0x20:
            start = flush()
            res.append('\\u%04x' % ord(c))
        i += 1

    flush()
    return ''.join(res)