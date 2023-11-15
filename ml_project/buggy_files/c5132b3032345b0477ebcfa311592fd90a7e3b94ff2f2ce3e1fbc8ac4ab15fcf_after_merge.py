def log_err(errmsg):
    """
    Prints/logs an error message to the server log.

    Args:
        errmsg (str): The message to be logged.

    """
    try:
        errmsg = str(errmsg)
    except Exception as e:
        errmsg = str(e)
    for line in errmsg.splitlines():
        log_msg('[EE] %s' % line)