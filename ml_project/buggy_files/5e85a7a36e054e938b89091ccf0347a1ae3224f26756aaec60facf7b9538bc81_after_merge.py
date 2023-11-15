def clean_args(args):
    """
    Cleans up the args that weren't passed in
    """
    for arg in list(args):
        if not args[arg]:
            del args[arg]
    return args