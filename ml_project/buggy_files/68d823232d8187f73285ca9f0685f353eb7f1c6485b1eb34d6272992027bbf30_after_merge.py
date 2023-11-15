    def set_nickname(self, value):
        """ The nickname you want to show to others.
        @param value A Unicode string.
        """
        # TODO(emilon): ugly hack to work around the fact that Tribler's config
        # system is really, really bad and can't deal with unicode strings by
        # itself. Fixing that at the ConfigParser level would break too many
        # things, so let's stick with this until we can throw the whole thing
        # away and use ConfigObj instead.
        self.sessconfig.set(u'general', u'nickname', u'"%s"' % value.strip('"'))