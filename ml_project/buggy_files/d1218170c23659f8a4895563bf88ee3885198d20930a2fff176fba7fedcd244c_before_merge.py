    def get_last_output(self, cmds=None):
        """Get output for last commands executed by ``run_command``

        :param cmds: Commands to get output for. Defaults to ``client.cmds``
        :type cmds: list(:py:class:`gevent.Greenlet`)

        :rtype: dict
        """
        cmds = self.cmds if cmds is None else cmds
        if cmds is None:
            return
        output = {}
        for cmd in self.cmds:
            self.get_output(cmd, output)
        return output