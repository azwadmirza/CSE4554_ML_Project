    def uids(self):
        try:
            real, effective, saved, _, _, _ = self._proc_cred()
        except AccessDenied:
            real = self._proc_basic_info()[proc_info_map['uid']]
            effective = self._proc_basic_info()[proc_info_map['euid']]
            saved = None
        return _common.puids(real, effective, saved)