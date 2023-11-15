def generate_id(prefix: Text = "", max_chars: Optional[int] = None) -> Text:
    """Generate a random UUID.

    Args:
        prefix: String to prefix the ID with.
        max_chars: Maximum number of characters.

    Returns:
        Generated random UUID.
    """
    import uuid

    gid = uuid.uuid4().hex
    if max_chars:
        gid = gid[:max_chars]

    return f"{prefix}{gid}"