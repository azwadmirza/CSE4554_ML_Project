def handle_exception(e):
    if isinstance(e, CondaExitZero):
        return 0
    elif isinstance(e, CondaError):
        from .base.context import context
        if context.debug or context.verbosity > 0:
            print_unexpected_error_message(e)
        else:
            print_conda_exception(e)
        return 1
    else:
        print_unexpected_error_message(e)
        return 1