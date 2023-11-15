def kill_tribler_process(process):
    """
    Kills the given process if it is a Tribler process.
    :param process: psutil.Process
    :return: None
    """
    def is_tribler_process(name):
        """
        Checks if the given name is of a Tribler processs. It checks a few potential keywords that
        could be present in a Tribler process name across different platforms.
        :param name: Process name
        :return: True if pid is a Tribler process else False
        """
        name = name.lower()
        process_keywords = ['usr/bin/python', 'run_tribler.py', 'tribler.exe', 'tribler.sh',
                            'Contents/MacOS/tribler', 'usr/bin/tribler']
        for keyword in process_keywords:
            if keyword.lower() in name:
                return True
        return False

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