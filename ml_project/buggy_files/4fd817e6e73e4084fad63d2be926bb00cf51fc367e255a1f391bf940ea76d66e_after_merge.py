    def track_labels(self) -> tuple:
        """ return track labels at the current time """
        labels, positions = self._manager.track_labels(self.current_time)

        # if there are no labels, return empty for vispy
        if not labels:
            return None, (None, None)

        padded_positions = self._pad_display_data(positions)
        return labels, padded_positions