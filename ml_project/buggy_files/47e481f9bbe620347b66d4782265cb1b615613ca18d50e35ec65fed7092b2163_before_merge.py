def run_command(source, filename=None):
    tree = hy_parse(source, filename=filename)
    __main__ = importlib.import_module('__main__')
    require("hy.cmdline", __main__, assignments="ALL")
    with filtered_hy_exceptions():
        hy_eval(tree, None, __main__, filename=filename, source=source)
    return 0