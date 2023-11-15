def _varargs(*args):
    """Encode var arguments to utf-8."""
    return [_handle_input(arg) for arg in args]