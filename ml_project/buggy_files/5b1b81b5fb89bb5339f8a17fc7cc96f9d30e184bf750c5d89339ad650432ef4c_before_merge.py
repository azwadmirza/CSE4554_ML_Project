    def _start_connection(self, variables):
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
        stdin = os.fdopen(master, 'wb', 0)
        os.close(slave)

        # Need to force a protocol that is compatible with both py2 and py3.
        # That would be protocol=2 or less.
        # Also need to force a protocol that excludes certain control chars as
        # stdin in this case is a pty and control chars will cause problems.
        # that means only protocol=0 will work.
        src = cPickle.dumps(self._play_context.serialize(), protocol=0)
        stdin.write(src)
        stdin.write(b'\n#END_INIT#\n')

        src = cPickle.dumps(variables, protocol=0)
        # remaining \r fail to round-trip the socket
        src = src.replace(b'\r', br'\r')
        stdin.write(src)
        stdin.write(b'\n#END_VARS#\n')

        stdin.flush()

        (stdout, stderr) = p.communicate()
        stdin.close()

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