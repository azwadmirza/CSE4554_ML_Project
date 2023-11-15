    def get_finished_label_text(self, started):
        """
        When an item finishes, returns a string displaying the start/end datetime range.
        started is a datetime object.
        """
        return self._get_label_text('gui_all_modes_transfer_finished', 'gui_all_modes_transfer_finished_range', started)