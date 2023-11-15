def run_command(source, filename=None):
    __main__ = importlib.import_module('__main__')
    require("hy.cmdline", __main__, assignments="ALL")
    try:
        tree = hy_parse(source, filename=filename)
    except HyLanguageError:
        hy_exc_handler(*sys.exc_info())
        return 1

    with filtered_hy_exceptions():
        hy_eval(tree, __main__.__dict__, __main__, filename=filename, source=source)
    return 0