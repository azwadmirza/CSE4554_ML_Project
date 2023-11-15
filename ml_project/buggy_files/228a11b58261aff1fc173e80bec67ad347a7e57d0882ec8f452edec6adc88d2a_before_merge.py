def runfile(filename=None, args=None, wdir=None, namespace=None,
            post_mortem=False, current_namespace=False):
    """
    Run filename
    args: command line arguments (string)
    wdir: working directory
    namespace: namespace for execution
    post_mortem: boolean, whether to enter post-mortem mode on error
    current_namespace: if true, run the file in the current namespace
    """
    ipython_shell = get_ipython()
    if filename is None:
        filename = get_current_file_name()
        if filename is None:
            return
    else:
        # get_debugger replaces \\ by / so we must undo that here
        # Otherwise code caching doesn't work
        if os.name == 'nt':
            filename = filename.replace('/', '\\')

    try:
        filename = filename.decode('utf-8')
    except (UnicodeError, TypeError, AttributeError):
        # UnicodeError, TypeError --> eventually raised in Python 2
        # AttributeError --> systematically raised in Python 3
        pass
    if PY2:
        filename = encode(filename)
    if __umr__.enabled:
        __umr__.run()
    if args is not None and not isinstance(args, basestring):
        raise TypeError("expected a character buffer object")
    try:
        file_code = get_file_code(filename)
    except Exception:
        _print(
            "This command failed to be executed because an error occurred"
            " while trying to get the file code from Spyder's"
            " editor. The error was:\n\n")
        get_ipython().showtraceback(exception_only=True)
        return
    if file_code is None:
        _print("Could not get code from editor.\n")
        return

    with NamespaceManager(filename, namespace, current_namespace,
                          file_code=file_code) as (ns_globals, ns_locals):
        sys.argv = [filename]
        if args is not None:
            for arg in shlex.split(args):
                sys.argv.append(arg)
        if wdir is not None:
            try:
                wdir = wdir.decode('utf-8')
            except (UnicodeError, TypeError, AttributeError):
                # UnicodeError, TypeError --> eventually raised in Python 2
                # AttributeError --> systematically raised in Python 3
                pass
            if os.path.isdir(wdir):
                os.chdir(wdir)
            else:
                _print("Working directory {} doesn't exist.\n".format(wdir))
        if post_mortem:
            set_post_mortem()

        if __umr__.has_cython:
            # Cython files
            with io.open(filename, encoding='utf-8') as f:
                ipython_shell.run_cell_magic('cython', '', f.read())
        else:
            exec_code(file_code, filename, ns_globals, ns_locals)

        clear_post_mortem()
        sys.argv = ['']