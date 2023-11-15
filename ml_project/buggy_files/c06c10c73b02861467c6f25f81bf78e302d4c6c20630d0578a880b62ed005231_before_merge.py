    def set_selinux_context(self, path, con):
        """
        Calls shell 'chcon' with 'path' and 'con' context.
        Returns exit result.
        """
        if self.is_selinux_system():
            return shellutil.run('chcon ' + con + ' ' + path)