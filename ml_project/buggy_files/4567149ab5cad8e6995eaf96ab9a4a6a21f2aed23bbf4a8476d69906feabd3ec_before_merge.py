    def get_nickname(self):
        """ Returns the set nickname.
        @return A Unicode string. """
        return unicode(self.sessconfig.get(u'general', u'nickname'))