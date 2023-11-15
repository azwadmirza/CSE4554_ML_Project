    def _on_data_change(self):
        self.node._need_colortransform_update = True
        self.node.set_data(self.layer._data_view)
        self.node.update()