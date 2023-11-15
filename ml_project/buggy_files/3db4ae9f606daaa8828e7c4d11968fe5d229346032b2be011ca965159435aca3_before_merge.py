    def can_delete(self, locale):
        return get_locale_usage(locale) == (0, 0)