def maybe_encode(text, encoding="utf8"):
    if is_py2:
        if isinstance(text, unicode):
            return text.encode(encoding)
        else:
            return text
    else:
        return text