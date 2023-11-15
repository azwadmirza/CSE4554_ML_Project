    def localized_draft(self):
        """
        Finds the translation in the current active language.

        If there is no translation in the active language, self is returned.

        Note: This will return translations that are in draft. If you want to exclude
        these, use the ``.localized`` attribute.
        """
        locale = Locale.get_active()

        if locale.id == self.locale_id:
            return self

        return self.get_translation_or_none(locale) or self