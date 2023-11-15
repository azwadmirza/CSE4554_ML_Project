    def _extract_sorting(self, limit):
        # Permissions entries are not stored with timestamp, so do not
        # force it.
        result = super()._extract_sorting(limit)
        without_last_modified = [s for s in result
                                 if s.field != self.model.modified_field]
        return without_last_modified