def _handle_input(arg):
    """Encode argument to utf-8 or fs encoding."""
    return encode(arg) if isinstance(arg, text_type) else arg