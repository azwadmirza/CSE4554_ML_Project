    def localized(self):
        """
        Finds the translation in the current active language.

        If there is no translation in the active language, self is returned.
        """
        locale = Locale.get_active()

        if locale.id == self.locale_id:
            return self

        return self.get_translation_or_none(locale) or self