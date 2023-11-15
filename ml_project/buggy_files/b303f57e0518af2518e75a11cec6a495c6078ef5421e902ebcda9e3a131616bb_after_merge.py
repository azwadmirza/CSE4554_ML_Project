    def _on_data_change(self, event=None):
        """ update the display """

        # update the shaders
        self.track_shader.current_time = self.layer.current_time
        self.graph_shader.current_time = self.layer.current_time

        # add text labels if they're visible
        if self.node._subvisuals[1].visible:
            labels_text, labels_pos = self.layer.track_labels
            self.node._subvisuals[1].text = labels_text
            self.node._subvisuals[1].pos = labels_pos

        self.node.update()
        # Call to update order of translation values with new dims:
        self._on_matrix_change()