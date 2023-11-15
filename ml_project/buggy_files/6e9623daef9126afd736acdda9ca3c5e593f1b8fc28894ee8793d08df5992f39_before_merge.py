    def __init__(self, parent, process = None, tty = False, wd = None, env = None, raw = True, *args, **kwargs):
        super(ssh_channel, self).__init__(*args, **kwargs)

        # keep the parent from being garbage collected in some cases
        self.parent = parent

        self.returncode = None
        self.host = parent.host
        self.tty  = tty
        self.env  = env
        self.process = process
        if isinstance(wd, six.text_type):
            wd = wd.encode('utf-8')
        self.cwd  = wd or b'.'

        env = env or {}
        msg = 'Opening new channel: %r' % (process or 'shell')

        if isinstance(process, (list, tuple)):
            process = b' '.join((lambda x:x.encode('utf-8') if isinstance(x, six.text_type) else x)(sh_string(s)) for s in process)
        if isinstance(process, six.text_type):
            process = process.encode('utf-8')

        if process and wd:
            process = b'cd ' + sh_string(wd) + b' >/dev/null 2>&1;' + process

        if process and env:
            for name, value in env.items():
                if not re.match('^[a-zA-Z_][a-zA-Z0-9_]*$', name):
                    self.error('run(): Invalid environment key %r' % name)
                export = 'export %s=%s;' % (name, sh_string(value))
                if isinstance(export, six.text_type):
                    export = export.encode('utf-8')
                process = export + process

        if process and tty:
            if raw:
                process = b'stty raw -ctlecho -echo; ' + process
            else:
                process = b'stty -ctlecho -echo; ' + process


        # If this object is enabled for DEBUG-level logging, don't hide
        # anything about the command that's actually executed.
        if process and self.isEnabledFor(logging.DEBUG):
            msg = 'Opening new channel: %r' % ((process,) or 'shell')

        with self.waitfor(msg) as h:
            import paramiko
            try:
                self.sock = parent.transport.open_session()
            except paramiko.ChannelException as e:
                if e.args == (1, 'Administratively prohibited'):
                    self.error("Too many sessions open! Use ssh_channel.close() or 'with'!")
                raise e

            if self.tty:
                self.sock.get_pty('xterm', term.width, term.height)

                def resizer():
                    if self.sock:
                        try:
                            self.sock.resize_pty(term.width, term.height)
                        except paramiko.ssh_exception.SSHException:
                            pass

                self.resizer = resizer
                term.term.on_winch.append(self.resizer)
            else:
                self.resizer = None

            # Put stderr on stdout. This might not always be desirable,
            # but our API does not support multiple streams
            self.sock.set_combine_stderr(True)

            self.settimeout(self.timeout)

            if process:
                self.sock.exec_command(process)
            else:
                self.sock.invoke_shell()

            h.success()