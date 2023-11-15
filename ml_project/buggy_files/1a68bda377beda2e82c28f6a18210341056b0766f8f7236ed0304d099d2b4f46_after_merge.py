def decode(value):
    """Decode to unicode."""
    return text_type(value, fs_encoding if valid_encoding else 'utf-8')