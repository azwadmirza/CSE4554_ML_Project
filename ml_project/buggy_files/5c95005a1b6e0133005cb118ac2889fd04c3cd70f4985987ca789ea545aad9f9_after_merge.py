def get_file(mod):
    f = None
    try:
        f = inspect.getsourcefile(mod) or inspect.getfile(mod)
    except:
        try:
            f = getattr(mod, '__file__', None)
        except:
            f = None
        if f and f.lower(f[-4:]) in ['.pyc', '.pyo']:
            filename = f[:-4] + '.py'
            if os.path.exists(filename):
                f = filename

    return f