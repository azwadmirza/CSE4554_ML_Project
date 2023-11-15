def exec_code(code, filename, ns_globals, ns_locals=None):
    """Execute code and display any exception."""
    global SHOW_INVALID_SYNTAX_MSG

    if PY2:
        filename = encode(filename)
        code = encode(code)

    ipython_shell = get_ipython()
    is_ipython = os.path.splitext(filename)[1] == '.ipy'
    try:
        if not is_ipython:
            # TODO: remove the try-except and let the SyntaxError raise
            # Because there should not be ipython code in a python file
            try:
                compiled = compile(code, filename, 'exec')
            except SyntaxError as e:
                try:
                    compiled = compile(transform_cell(code), filename, 'exec')
                except SyntaxError:
                    if PY2:
                        raise e
                    else:
                        # Need to call exec to avoid Syntax Error in Python 2.
                        # TODO: remove exec when dropping Python 2 support.
                        exec("raise e from None")
                else:
                    if SHOW_INVALID_SYNTAX_MSG:
                        _print(
                            "\nWARNING: This is not valid Python code. "
                            "If you want to use IPython magics, "
                            "flexible indentation, and prompt removal, "
                            "please save this file with the .ipy extension. "
                            "This will be an error in a future version of "
                            "Spyder.\n")
                        SHOW_INVALID_SYNTAX_MSG = False
        else:
            compiled = compile(transform_cell(code), filename, 'exec')

        exec(compiled, ns_globals, ns_locals)
    except SystemExit as status:
        # ignore exit(0)
        if status.code:
            ipython_shell.showtraceback(exception_only=True)
    except BaseException as error:
        if (isinstance(error, bdb.BdbQuit)
                and ipython_shell.kernel._pdb_obj):
            # Ignore BdbQuit if we are debugging, as it is expected.
            ipython_shell.kernel._pdb_obj = None
        else:
            # We ignore the call to exec
            ipython_shell.showtraceback(tb_offset=1)