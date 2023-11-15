    def _requires_user_interaction(self):
        baseurl = self._tab.url()
        url = self.resolve_url(baseurl)
        if url is None:
            return True
        return url.scheme() not in urlutils.WEBENGINE_SCHEMES