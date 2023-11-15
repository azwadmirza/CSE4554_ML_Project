    def _on_contrast_limits_change(self):
        if self.layer.dims.ndisplay == 3:
            self._on_data_change()
        else:
            self.node.clim = self.layer.contrast_limits