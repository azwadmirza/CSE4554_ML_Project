def set_target(kind, parser=(lambda x: x), positional=False):
    def do(arg, it):
        options.target_kind = kind
        options.target = parser(arg if positional else next(it))

    return do