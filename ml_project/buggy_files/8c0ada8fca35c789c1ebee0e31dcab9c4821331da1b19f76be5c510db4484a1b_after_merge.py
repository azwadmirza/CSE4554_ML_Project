def b64decode(string):
    return to_text(base64.b64decode(to_bytes(string, errors='surrogate_or_strict')))