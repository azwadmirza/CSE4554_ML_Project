    def __init__(self, host, cmd, channel, stdout, stderr, stdin,
                 exit_code=None, exception=None):
        """
        :param host: Host name output is for
        :type host: str
        :param cmd: Command execution object
        :type cmd: :py:class:`gevent.Greenlet`
        :param channel: SSH channel used for command execution
        :type channel: :py:class:`socket.socket` compatible object
        :param stdout: Standard output buffer
        :type stdout: generator
        :param stderr: Standard error buffer
        :type stderr: generator
        :param stdin: Standard input buffer
        :type stdin: :py:func:`file`-like object
        :param exit_code: Exit code of command
        :type exit_code: int or None
        :param exception: Exception from host if any
        :type exception: :py:class:`Exception` or ``None``
        """
        super(HostOutput, self).__init__(
            (('host', host), ('cmd', cmd), ('channel', channel),
             ('stdout', stdout), ('stderr', stderr),
             ('stdin', stdin), ('exit_code', exit_code),
             ('exception', exception)))
        self.host = host
        self.cmd = cmd
        self.channel = channel
        self.stdout = stdout
        self.stderr = stderr
        self.stdin = stdin
        self.exception = exception
        self.exit_code = exit_code