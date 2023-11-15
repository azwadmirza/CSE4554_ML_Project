    def _recache(self):
        global _SESSIONS
        if not _SESSIONS:
            from evennia.server.sessionhandler import SESSIONS as _SESSIONS
        self._sessid_cache = list(set(int(val) for val in (self.obj.db_sessid or "").split(",") if val))
        if any(sessid for sessid in self._sessid_cache if sessid not in _SESSIONS):
            # cache is out of sync with sessionhandler! Only retain the ones in the handler.
            self._sessid_cache = [sessid for sessid in self._sessid_cache if sessid in _SESSIONS]
            self.obj.db_sessid = ",".join(str(val) for val in self._sessid_cache)
            self.obj.save(update_fields=["db_sessid"])