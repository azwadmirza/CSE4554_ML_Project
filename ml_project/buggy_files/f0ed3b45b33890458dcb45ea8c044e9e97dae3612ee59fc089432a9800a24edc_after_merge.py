    def discard_changes(self, *args, **kwargs):
        self.send_command(b'exit discard')