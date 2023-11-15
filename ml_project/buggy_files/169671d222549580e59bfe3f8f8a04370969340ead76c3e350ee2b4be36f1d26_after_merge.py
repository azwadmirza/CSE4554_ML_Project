    def track_labels(self, current_time: int) -> tuple:
        """ return track labels at the current time """
        # this is the slice into the time ordered points array
        if current_time not in self._points_lookup:
            return [], []

        lookup = self._points_lookup[current_time]
        pos = self._points[lookup, ...]
        lbl = [f'ID:{i}' for i in self._points_id[lookup]]
        return lbl, pos