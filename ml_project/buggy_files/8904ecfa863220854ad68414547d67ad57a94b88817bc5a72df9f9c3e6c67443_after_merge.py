    def gids(self):
        try:
            _, _, _, real, effective, saved = self._proc_cred()
        except AccessDenied:
            real = self._proc_basic_info()[proc_info_map['gid']]
            effective = self._proc_basic_info()[proc_info_map['egid']]
            saved = None
        return _common.puids(real, effective, saved)