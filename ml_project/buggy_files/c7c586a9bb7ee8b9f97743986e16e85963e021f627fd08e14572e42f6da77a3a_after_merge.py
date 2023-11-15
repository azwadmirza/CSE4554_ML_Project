def _varargs(*args):
    """Encode var arguments to utf-8 or fs encoding."""
    return [_handle_input(arg) for arg in args]