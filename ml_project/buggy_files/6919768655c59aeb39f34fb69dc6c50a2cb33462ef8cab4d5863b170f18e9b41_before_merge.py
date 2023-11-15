    def _on_data_change(self):
        if self.layer.dims.ndisplay == 3:
            self.node.set_data(
                self.layer._data_view,
                contrast_limits=self.layer.contrast_limits,
            )
        else:
            self.node._need_colortransform_update = True
            self.node.set_data(self.layer._data_view)
        self.node.update()