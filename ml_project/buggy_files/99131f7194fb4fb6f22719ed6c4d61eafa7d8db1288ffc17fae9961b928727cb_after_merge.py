def _verify_encodings(encodings):
    """Checks the encoding to ensure proper format"""
    if encodings is not None and not isinstance(encodings, list):
        return [encodings]

    return encodings