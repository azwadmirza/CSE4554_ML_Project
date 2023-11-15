    def set_caps(self, data):
        """Set caps."""
        if not data:
            return

        def _parse_cap(tag):
            elm = data.find(tag)
            return elm.get('supportedparams').split(',') if elm and elm.get('available') == 'yes' else []

        self.cap_tv_search = _parse_cap('tv-search')