def kill_tribler_process(process):
    """
    Kills the given process if it is a Tribler process.
    :param process: psutil.Process
    :return: None
    """

    try:
        if not is_tribler_process(process.exe()):
            return

        parent_process = process.parent()
        if parent_process.pid > 1 and is_tribler_process(parent_process.exe()):
            os.kill(process.pid, 9)
            os.kill(parent_process.pid, 9)
        else:
            os.kill(process.pid, 9)

    except OSError:
        logging.exception("Failed to kill the existing Tribler process")