    def get_session_settings(self, lt_session):
        return deepcopy(self.ltsettings.get(lt_session, {}))