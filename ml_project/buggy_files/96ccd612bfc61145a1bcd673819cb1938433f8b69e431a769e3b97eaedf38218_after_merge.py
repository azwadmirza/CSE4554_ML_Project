    def _supportsUrl(cls, url, export=False):
        return url.scheme.lower() in ('wasb', 'wasbs')