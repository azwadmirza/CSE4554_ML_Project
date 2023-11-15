    def set_data(self, data):
        self.data, old_data = data, self.data
        self.selection = None
        self._set_input_summary()

        self.controls.normalize.setDisabled(
            bool(self.data) and sp.issparse(self.data.X))

        # Do not needlessly recluster the data if X hasn't changed
        if old_data and self.data and array_equal(self.data.X, old_data.X):
            if self.auto_commit:
                self.send_data()
        else:
            self.invalidate(unconditional=True)