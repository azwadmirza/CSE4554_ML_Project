    def _extract_sorting(self, limit):
        # Permissions entries are not stored with timestamp, so do not
        # force it.
        result = super()._extract_sorting(limit)
        without_last_modified = [s for s in result
                                 if s.field != self.model.modified_field]
        # For pagination, there must be at least one sort criteria.
        # We use ``uri`` because its values are unique.
        if "uri" not in [s.field for s in without_last_modified]:
            without_last_modified.append(Sort("uri", -1))
        return without_last_modified