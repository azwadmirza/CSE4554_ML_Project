def encode(value):
    """Encode to bytes."""
    return value.encode(fs_encoding if valid_encoding else 'utf-8')