def make_closure(f, handle_arg=None, handle_output=None):
    """Apply an input handler and output handler to a function.

    Used to ensure UTF-8 encoding at input and output.
    """
    return patch_output(patch_input(f, handle_arg), handle_output)