    def track_labels(self) -> tuple:
        """ return track labels at the current time """

        # check that current time is still within the frame map
        if self.current_time < 0 or self.current_time > self._manager.max_time:
            # need to return a tuple for pos to clear the vispy text visual
            return None, (None, None)

        labels, positions = self._manager.track_labels(self.current_time)
        padded_positions = self._pad_display_data(positions)
        return labels, padded_positions