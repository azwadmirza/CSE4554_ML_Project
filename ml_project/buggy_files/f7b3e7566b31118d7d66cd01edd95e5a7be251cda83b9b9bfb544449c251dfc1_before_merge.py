def generate_id(prefix: Text = "", max_chars: Optional[int] = None) -> Text:
    import uuid

    gid = uuid.uuid4().hex
    if max_chars:
        gid = gid[:max_chars]

    return f"{prefix}{gid}"