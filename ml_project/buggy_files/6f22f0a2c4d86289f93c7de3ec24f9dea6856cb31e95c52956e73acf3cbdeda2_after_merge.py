def system(cmd):
    """Win32 version of os.system() that works with network shares.

    Note that this implementation returns None, as meant for use in IPython.

    Parameters
    ----------
    cmd : str
      A command to be executed in the system shell.

    Returns
    -------
    None : we explicitly do NOT return the subprocess status code, as this
    utility is meant to be used extensively in IPython, where any return value
    would trigger :func:`sys.displayhook` calls.
    """
    # The controller provides interactivity with both
    # stdin and stdout
    #import _process_win32_controller
    #_process_win32_controller.system(cmd)

    with AvoidUNCPath() as path:
        if path is not None:
            cmd = '"pushd %s &&"%s' % (path, cmd)
        return process_handler(cmd, _system_body)