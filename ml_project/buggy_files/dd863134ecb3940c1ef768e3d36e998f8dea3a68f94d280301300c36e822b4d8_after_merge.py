    def pipe_wait(self, child_conn):
        """
        This method is executed in a separate thread and is only here since there are some calls that are crashing on
        macOS in a subprocess (due to libdispatch.dylib).
        """
        while True:
            try:
                cmd, arg = child_conn.recv()
                if cmd == "get_keyring_password":
                    child_conn.send(keyring.get_password('tribler', arg['username']))
                elif cmd == "set_keyring_password":
                    keyring.set_password('tribler', arg['username'], arg['password'])
                    child_conn.send('done')
            except EOFError:
                time.sleep(2)  # We can safely do this since we're on a separate thread