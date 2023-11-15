    def get_last_output(self, cmds=None, greenlet_timeout=None,
                        return_list=False):
        """Get output for last commands executed by ``run_command``

        :param cmds: Commands to get output for. Defaults to ``client.cmds``
        :type cmds: list(:py:class:`gevent.Greenlet`)
        :param greenlet_timeout: (Optional) Greenlet timeout setting.
          Defaults to no timeout. If set, this function will raise
          :py:class:`gevent.Timeout` after ``greenlet_timeout`` seconds
          if no result is available from greenlets.
          In some cases, such as when using proxy hosts, connection timeout
          is controlled by proxy server and getting result from greenlets may
          hang indefinitely if remote server is unavailable. Use this setting
          to avoid blocking in such circumstances.
          Note that ``gevent.Timeout`` is a special class that inherits from
          ``BaseException`` and thus **can not be caught** by
          ``stop_on_errors=False``.
        :type greenlet_timeout: float
        :param return_list: (Optional) Return a list of ``HostOutput`` objects
          instead of dictionary. ``run_command`` will return a list starting
          from 2.0.0 - enable this flag to avoid client code breaking on
          upgrading to 2.0.0.
        :type return_list: bool

        :rtype: dict or list
        """
        cmds = self.cmds if cmds is None else cmds
        if cmds is None:
            return
        if not return_list:
            warn(_output_depr_notice)
            output = {}
            for cmd in self.cmds:
                self.get_output(cmd, output, timeout=greenlet_timeout)
            return output
        return [self._get_output_from_greenlet(cmd, timeout=greenlet_timeout)
                for cmd in cmds]