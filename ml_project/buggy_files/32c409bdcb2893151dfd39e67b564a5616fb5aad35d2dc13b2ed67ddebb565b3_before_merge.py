def encode(value):
    """Encode to bytes."""
    return value.encode('utf-8' if os.name != 'nt' else fs_encoding)