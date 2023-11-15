def run_icommand(source, **kwargs):
    if os.path.exists(source):
        # Emulate Python cmdline behavior by setting `sys.path` relative
        # to the executed file's location.
        if sys.path[0] == '':
            sys.path[0] = os.path.realpath(os.path.split(source)[0])
        else:
            sys.path.insert(0, os.path.split(source)[0])

        with io.open(source, "r", encoding='utf-8') as f:
            source = f.read()
        filename = source
    else:
        filename = '<string>'

    hr = HyREPL(**kwargs)
    with filtered_hy_exceptions():
        res = hr.runsource(source, filename=filename)

    # If the command was prematurely ended, show an error (just like Python
    # does).
    if res:
        hy_exc_handler(sys.last_type, sys.last_value, sys.last_traceback)

    return run_repl(hr)