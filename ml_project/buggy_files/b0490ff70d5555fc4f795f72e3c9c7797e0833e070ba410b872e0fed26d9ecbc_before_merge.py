def make_closure(f, handle_arg, handle_output):
    """Create a closure that encodes parameters to utf-8 and call original function."""
    return lambda *args, **kwargs: handle_output(f(*[handle_arg(arg) for arg in args], **{k: handle_arg(arg) for k, arg in kwargs.items()}))