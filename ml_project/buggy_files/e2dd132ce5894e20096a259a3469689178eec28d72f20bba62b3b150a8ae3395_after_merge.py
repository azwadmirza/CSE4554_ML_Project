    def set_session_settings(self, lt_session, new_settings):
        """
        Apply/set new sessions in a libtorrent session.
        :param lt_session: The libtorrent session to apply the settings to.
        :param new_settings: The new settings to apply.
        """

        # Keeping a copy of the settings because subsequent calls to get_settings are likely to fail
        # when libtorrent will try to decode peer_fingerprint to unicode.
        if lt_session not in self.ltsettings:
            self.ltsettings[lt_session] = lt_session.get_settings()
        self.ltsettings[lt_session].update(new_settings)

        try:
            if hasattr(lt_session, "apply_settings"):
                lt_session.apply_settings(new_settings)
            else:
                lt_session.set_settings(new_settings)
        except OverflowError:
            raise OverflowError("Overflow error when setting libtorrent sessions with settings: %s" % new_settings)