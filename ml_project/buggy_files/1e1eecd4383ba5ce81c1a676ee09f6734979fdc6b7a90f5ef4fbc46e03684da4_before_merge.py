def can_init():
    """This function returns True iff stderr is a TTY and we are not inside a
    REPL.  Iff this function returns `True`, a call to :meth:`init` will let
    ``pwnlib`` manage the terminal.
    """

    if sys.platform == 'win32':
        return False

    if not sys.stdout.isatty():
        return False

    # Check for python -i
    if sys.flags.interactive:
        return False

    # Check fancy REPLs
    mods = sys.modules.keys()
    for repl in ['IPython', 'bpython', 'dreampielib']:
        if repl in mods:
            return False

    # The standard python REPL will have co_filename == '<stdin>' for some
    # frame. We raise an exception to set sys.exc_info so we can unwind the call
    # stack.
    try:
        raise BaseException
    except BaseException:
        frame = sys.exc_info()[2].tb_frame

    while frame:
        if frame.f_code.co_filename == '<stdin>':
            return False
        frame = frame.f_back

    return True