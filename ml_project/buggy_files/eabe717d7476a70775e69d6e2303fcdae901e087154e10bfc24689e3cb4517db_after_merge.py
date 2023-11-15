    def _on_data_change(self, event=None):
        # Check if ndisplay has changed current node type needs updating
        if (
            self.layer.dims.ndisplay == 3 and len(self.node._subvisuals) != 2
        ) or (
            self.layer.dims.ndisplay == 2 and len(self.node._subvisuals) != 3
        ):
            self._on_display_change()
            self._on_highlight_change()

        if len(self.layer._data_view) > 0:
            edge_color = self.layer.edge_color[self.layer._indices_view]
            face_color = self.layer.face_color[self.layer._indices_view]
        else:
            edge_color = np.array([[0.0, 0.0, 0.0, 1.0]], dtype=np.float32)
            face_color = np.array([[1.0, 1.0, 1.0, 1.0]], dtype=np.float32)

        # Set vispy data, noting that the order of the points needs to be
        # reversed to make the most recently added point appear on top
        # and the rows / columns need to be switch for vispys x / y ordering
        if len(self.layer._data_view) == 0:
            data = np.zeros((1, self.layer.dims.ndisplay))
            size = [0]
        else:
            data = self.layer._data_view
            size = self.layer._size_view

        set_data = self.node._subvisuals[0].set_data

        set_data(
            data[:, ::-1] + 0.5,
            size=size,
            edge_width=self.layer.edge_width,
            symbol=self.layer.symbol,
            edge_color=edge_color,
            face_color=face_color,
            scaling=True,
        )
        self.node.update()