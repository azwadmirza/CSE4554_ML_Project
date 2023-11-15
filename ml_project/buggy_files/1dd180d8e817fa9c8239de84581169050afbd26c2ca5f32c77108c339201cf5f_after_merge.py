def set_target(kind, parser=(lambda x: x), positional=False):
    def do(arg, it):
        options.target_kind = kind
        target = parser(arg if positional else next(it))

        if isinstance(target, bytes):
            # target may be the code, so, try some additional encodings...
            try:
                target = target.decode(sys.getfilesystemencoding())
            except UnicodeDecodeError:
                try:
                    target = target.decode("utf-8")
                except UnicodeDecodeError:
                    import locale

                    target = target.decode(locale.getpreferredencoding(False))
        options.target = target

    return do