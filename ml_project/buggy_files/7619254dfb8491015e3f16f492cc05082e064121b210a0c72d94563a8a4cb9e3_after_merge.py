    def _on_tracks_change(self, event=None):
        """ update the shader when the track data changes """

        self.track_shader.use_fade = self.layer.use_fade
        self.track_shader.tail_length = self.layer.tail_length
        self.track_shader.vertex_time = self.layer.track_times

        # change the data to the vispy line visual
        self.node._subvisuals[0].set_data(
            pos=self.layer._view_data,
            connect=self.layer.track_connex,
            width=self.layer.tail_width,
            color=self.layer.track_colors,
        )

        # Call to update order of translation values with new dims:
        self._on_matrix_change()