    def _start_connection(self):
        '''
        Starts the persistent connection
        '''
        master, slave = pty.openpty()
        p = subprocess.Popen(["ansible-connection", to_text(os.getppid())], stdin=slave, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

        (stdout, stderr) = p.communicate()
        stdin.close()

        if p.returncode == 0:
            result = json.loads(to_text(stdout, errors='surrogate_then_replace'))
        else:
            result = json.loads(to_text(stderr, errors='surrogate_then_replace'))

        if 'messages' in result:
            for msg in result.get('messages'):
                display.vvvv('%s' % msg, host=self._play_context.remote_addr)

        if 'error' in result:
            if self._play_context.verbosity > 2:
                msg = "The full traceback is:\n" + result['exception']
                display.display(result['exception'], color=C.COLOR_ERROR)
            raise AnsibleError(result['error'])

        return result['socket_path']