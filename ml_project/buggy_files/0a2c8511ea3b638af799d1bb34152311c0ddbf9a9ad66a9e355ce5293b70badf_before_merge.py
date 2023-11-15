def parse_quotes(cmd, quotes=True, string=True):
    """ parses quotes """
    import shlex

    if quotes:
        args = shlex.split(cmd)
    else:
        args = cmd.split()

    if string:
        str_args = []
        for arg in args:
            str_args.append(str(arg))
        return str_args
    return args