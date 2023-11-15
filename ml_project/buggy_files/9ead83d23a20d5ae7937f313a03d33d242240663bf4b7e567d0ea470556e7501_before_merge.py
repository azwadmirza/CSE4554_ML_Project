    def _process_remote(self, host, path, user):
        transport = self._play_context.connection
        if host not in C.LOCALHOST or transport != "local":
            return self._format_rsync_rsh_target(host, path, user)

        if ':' not in path and not path.startswith('/'):
            path = self._get_absolute_path(path=path)
        return path