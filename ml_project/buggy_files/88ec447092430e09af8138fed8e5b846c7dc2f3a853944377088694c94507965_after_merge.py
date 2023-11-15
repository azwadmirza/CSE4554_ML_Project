    def _round(self, freq, rounder, ambiguous):
        # round the local times
        values = _ensure_datetimelike_to_i8(self)
        result = round_ns(values, rounder, freq)
        result = self._maybe_mask_results(result, fill_value=NaT)

        attribs = self._get_attributes_dict()
        if 'freq' in attribs:
            attribs['freq'] = None
        if 'tz' in attribs:
            attribs['tz'] = None
        return self._ensure_localized(
            self._shallow_copy(result, **attribs), ambiguous
        )