def main(*args):
    if not args:
        args = sys.argv

    args = tuple(_ensure_text_type(s) for s in args)

    log.debug("conda.cli.main called with %s", args)
    if len(args) > 1:
        try:
            argv1 = args[1].strip()
            if argv1.startswith('..'):
                import conda.cli.activate as activate
                activate.main()
                return
            if argv1 in ('activate', 'deactivate'):
                from ..exceptions import CommandNotFoundError
                raise CommandNotFoundError(argv1)
        except Exception as e:
            from ..exceptions import handle_exception
            return handle_exception(e)

    from ..exceptions import conda_exception_handler
    return conda_exception_handler(_main, *args)