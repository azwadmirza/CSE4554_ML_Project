def main(*args):
    if not args:
        args = sys.argv

    if not args:
        args = sys.argv

    log.debug("conda.cli.main called with %s", args)
    if len(args) > 1:
        try:
            argv1 = args[1].strip()
            if argv1.startswith('..'):
                import conda.cli.activate as activate
                activate.main()
                return
            if argv1 in ('activate', 'deactivate'):

                message = "'%s' is not a conda command.\n" % argv1
                from ..common.compat import on_win
                if not on_win:
                    message += ' Did you mean "source %s" ?\n' % ' '.join(args[1:])

                from ..exceptions import CommandNotFoundError
                raise CommandNotFoundError(argv1, message)
        except Exception as e:
            from ..exceptions import handle_exception
            return handle_exception(e)

    from ..exceptions import conda_exception_handler
    return conda_exception_handler(_main, *args)