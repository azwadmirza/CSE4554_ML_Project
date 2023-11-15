    def get_nickname(self):
        """ Returns the set nickname.
        @return A Unicode string. """
        return self.sessconfig.get(u'general', u'nickname')