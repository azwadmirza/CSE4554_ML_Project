    def get_event(self, href, calendar):
        return self._cover_event(self._backend.get(href, calendar))