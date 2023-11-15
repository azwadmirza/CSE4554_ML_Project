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
        filename = '<input>'

    with filtered_hy_exceptions():
        hr = HyREPL(**kwargs)
        hr.runsource(source, filename=filename, symbol='single')
        return run_repl(hr)