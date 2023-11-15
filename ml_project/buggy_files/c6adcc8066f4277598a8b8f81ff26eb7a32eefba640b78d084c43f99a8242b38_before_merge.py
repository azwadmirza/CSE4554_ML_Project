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