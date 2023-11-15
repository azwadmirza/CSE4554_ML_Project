    def __init__(self, logfile_path: str) -> None:
        """
        Create output handle

        :param logfile_path: Path or string file path or "-" for stdout
        """

        # Fail if current working directory does not exist so we don't crash in
        # standard library path-handling code.
        try:
            os.getcwd()
        except OSError:
            exit("T: Error: Current working directory does not exist.")

        if logfile_path == "-":
            self.logfile = sys.stdout
        else:
            # Log file path should be absolute since some processes may run in
            # different directories:
            logfile_path = os.path.abspath(logfile_path)
            self.logfile = _open_logfile(logfile_path)
        self.logfile_path = logfile_path

        self.start_time = curtime()
        self.logtail = deque(maxlen=25)  # type: deque  # keep last 25 lines

        self.write(
            "Telepresence {} launched at {}".format(__version__, ctime())
        )
        self.write("  {}".format(str_command(sys.argv)))
        if version_override:
            self.write("  TELEPRESENCE_VERSION is {}".format(image_version))
        elif image_version != __version__:
            self.write("  Using images version {} (dev)".format(image_version))