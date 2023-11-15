def main(*args):
    # conda.common.compat contains only stdlib imports
    from ..common.compat import ensure_text_type  # , init_std_stream_encoding

    # init_std_stream_encoding()
    if not args:
        args = sys.argv

    args = tuple(ensure_text_type(s) for s in args)

    if len(args) > 1:
        try:
            argv1 = args[1].strip()
            if argv1.startswith('shell.'):
                from ..activate import main as activator_main
                return activator_main()
            elif argv1.startswith('..'):
                import conda.cli.activate as activate
                activate.main()
                return
            elif argv1 in ('activate', 'deactivate'):
                from ..exceptions import CommandNotFoundError
                raise CommandNotFoundError(argv1)
        except Exception as e:
            _, exc_val, exc_tb = sys.exc_info()
            init_loggers()
            from ..exceptions import ExceptionHandler
            return ExceptionHandler().handle_exception(exc_val, exc_tb)

    from ..exceptions import conda_exception_handler
    return conda_exception_handler(_main, *args)