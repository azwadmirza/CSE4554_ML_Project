    def prepare(self):
        """ Initialize important variables """
        if not hasattr(self, "HOSTER_NAME"):
            self.HOSTER_NAME = re.search(self.__pattern__, self.pyfile.url).group(1)
        if not hasattr(self, "DIRECT_LINK_PATTERN"):
            self.DIRECT_LINK_PATTERN = r'(http://([^/]*?%s|\d+\.\d+\.\d+\.\d+)(:\d+/d/|/files/\d+/\w+/)[^"\'<]+)' % self.HOSTER_NAME

        self.captcha = self.errmsg = None
        self.passwords = self.getPassword().splitlines()