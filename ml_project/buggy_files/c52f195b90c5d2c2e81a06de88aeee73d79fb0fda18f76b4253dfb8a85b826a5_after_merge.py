    def _start_connection(self):
        '''
        Starts the persistent connection
        '''
        master, slave = pty.openpty()

        python = sys.executable

        def find_file_in_path(filename):
            # Check $PATH first, followed by same directory as sys.argv[0]
            paths = os.environ['PATH'].split(os.pathsep) + [os.path.dirname(sys.argv[0])]
            for dirname in paths:
                fullpath = os.path.join(dirname, filename)
                if os.path.isfile(fullpath):
                    return fullpath

            raise AnsibleError("Unable to find location of '%s'" % filename)

        p = subprocess.Popen(
            [python, find_file_in_path('ansible-connection'), to_text(os.getppid())],
            stdin=slave, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        os.close(slave)

        # We need to set the pty into noncanonical mode. This ensures that we
        # can receive lines longer than 4095 characters (plus newline) without
        # truncating.
        old = termios.tcgetattr(master)
        new = termios.tcgetattr(master)
        new[3] = new[3] & ~termios.ICANON

        try:
            termios.tcsetattr(master, termios.TCSANOW, new)
            write_to_file_descriptor(master, {'ansible_command_timeout': self.get_option('persistent_command_timeout')})
            write_to_file_descriptor(master, self._play_context.serialize())

            (stdout, stderr) = p.communicate()
        finally:
            termios.tcsetattr(master, termios.TCSANOW, old)
        os.close(master)

        if p.returncode == 0:
            result = json.loads(to_text(stdout, errors='surrogate_then_replace'))
        else:
            try:
                result = json.loads(to_text(stderr, errors='surrogate_then_replace'))
            except getattr(json.decoder, 'JSONDecodeError', ValueError):
                # JSONDecodeError only available on Python 3.5+
                result = {'error': to_text(stderr, errors='surrogate_then_replace')}

        if 'messages' in result:
            for msg in result.get('messages'):
                display.vvvv('%s' % msg, host=self._play_context.remote_addr)

        if 'error' in result:
            if self._play_context.verbosity > 2:
                if result.get('exception'):
                    msg = "The full traceback is:\n" + result['exception']
                    display.display(msg, color=C.COLOR_ERROR)
            raise AnsibleError(result['error'])

        return result['socket_path']