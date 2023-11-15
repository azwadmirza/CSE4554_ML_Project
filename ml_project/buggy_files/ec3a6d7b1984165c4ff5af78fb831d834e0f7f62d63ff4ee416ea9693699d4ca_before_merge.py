def maybe_encode(text, encoding="utf8"):
    if is_py2:
        return text.encode(encoding)
    else:
        return text