    def _on_contrast_limits_change(self):
        if self.layer.dims.ndisplay == 3:
            self.node.set_data(
                self.layer._data_view,
                contrast_limits=self.layer.contrast_limits,
            )
        else:
            self.node.clim = self.layer.contrast_limits