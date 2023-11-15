    def can_delete(self, locale):
        if not self.queryset.exclude(pk=locale.pk).exists():
            self.cannot_delete_message = gettext_lazy(
                "This locale cannot be deleted because there are no other locales."
            )
            return False

        if get_locale_usage(locale) != (0, 0):
            self.cannot_delete_message = gettext_lazy(
                "This locale cannot be deleted because there are pages and/or other objects using it."
            )
            return False

        return True