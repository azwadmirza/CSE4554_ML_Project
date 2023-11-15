def _handle_input(arg):
    """Encode argument to utf-8."""
    # on windows the input params for fs operations needs to be encoded using fs encoding
    return arg.encode('utf-8' if os.name != 'nt' else fs_encoding) if isinstance(arg, text_type) else arg