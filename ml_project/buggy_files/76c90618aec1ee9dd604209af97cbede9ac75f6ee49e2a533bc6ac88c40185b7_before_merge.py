def _handle_input(arg):
    """Encode argument to utf-8 or fs encoding."""
    # on windows the input params for fs operations needs to be encoded using fs encoding
    return encode(arg) if isinstance(arg, text_type) else arg