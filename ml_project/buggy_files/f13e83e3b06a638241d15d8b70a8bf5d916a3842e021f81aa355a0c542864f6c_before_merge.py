def spinner(message=None, enabled=True, json=False):
    """
    Args:
        message (str, optional):
            An optional message to prefix the spinner with.
            If given, ': ' are automatically added.
        enabled (bool):
            If False, usage is a no-op.
        json (bool):
           If True, will not output non-json to stdout.

    """
    sp = Spinner(enabled)
    exception_raised = False
    try:
        if message:
            if json:
                pass
            else:
                sys.stdout.write("%s: " % message)
                sys.stdout.flush()
        if not json:
            sp.start()
        yield
    except:
        exception_raised = True
        raise
    finally:
        if not json:
            sp.stop()
        if message:
            if json:
                pass
            else:
                if exception_raised:
                    sys.stdout.write("failed\n")
                else:
                    sys.stdout.write("done\n")
                sys.stdout.flush()