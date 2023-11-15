def parse_quotes(cmd, quotes=True, string=True):
    """ parses quotes """
    import shlex

    try:
        args = shlex.split(cmd) if quotes else cmd.split()
    except ValueError as exception:
        logger.error(exception)
        return []

    return [str(arg) for arg in args] if string else args