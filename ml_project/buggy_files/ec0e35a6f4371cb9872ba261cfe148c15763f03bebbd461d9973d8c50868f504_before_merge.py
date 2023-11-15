    def discard_changes(self, rollback_id=None):
        command = b'rollback'
        if rollback_id is not None:
            command += b' %s' % int(rollback_id)
        for cmd in chain(to_list(command), b'exit'):
            self.send_command(cmd)