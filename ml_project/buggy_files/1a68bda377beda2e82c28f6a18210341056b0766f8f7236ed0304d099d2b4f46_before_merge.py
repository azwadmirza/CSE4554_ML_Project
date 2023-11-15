def decode(value):
    """Decode to unicode."""
    # on windows the returned info from fs operations needs to be decoded using fs encoding
    return text_type(value, 'utf-8' if os.name != 'nt' else fs_encoding)