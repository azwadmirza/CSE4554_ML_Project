    def _supportsUrl(cls, url, export=False):
        return url.scheme.lower() == 'wasb' or url.scheme.lower() == 'wasbs'