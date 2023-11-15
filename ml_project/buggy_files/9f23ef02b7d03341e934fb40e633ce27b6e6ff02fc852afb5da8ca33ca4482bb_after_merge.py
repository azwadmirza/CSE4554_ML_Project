def xonfig(args, stdin=None):
    """Runs the xonsh configuration utility."""
    from xonsh.xonfig import xonfig_main  # lazy import
    return xonfig_main(args)