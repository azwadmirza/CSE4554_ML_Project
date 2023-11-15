    def discard_changes(self):
        command = b'rollback 0'
        for cmd in chain(to_list(command), b'exit'):
            self.send_command(cmd)