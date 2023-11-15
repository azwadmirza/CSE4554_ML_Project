def b64encode(string):
    return to_text(base64.b64encode(to_bytes(string, errors='surrogate_or_strict')))