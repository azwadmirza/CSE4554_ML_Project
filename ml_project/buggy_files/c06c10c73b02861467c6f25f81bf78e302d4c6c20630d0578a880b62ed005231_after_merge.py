    def set_selinux_context(self, path, con):
        """
        Calls shell 'chcon' with 'path' and 'con' context.
        Returns exit result.
        """
        if self.is_selinux_system():
            if not os.path.exists(path):
                logger.error("Path does not exist: {0}".format(path))
                return 1
            return shellutil.run('chcon ' + con + ' ' + path)