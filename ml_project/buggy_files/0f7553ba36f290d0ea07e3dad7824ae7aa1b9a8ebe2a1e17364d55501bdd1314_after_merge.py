    def on_draw(self, event):
        """Called whenever the canvas is drawn.

        This is triggered from vispy whenever new data is sent to the canvas or
        the camera is moved and is connected in the `QtViewer`.
        """
        self.layer.scale_factor = self.scale_factor
        old_corner_pixels = self.layer.corner_pixels
        self.layer.corner_pixels = self.coordinates_of_canvas_corners()

        # For 2D multiscale data determine if new data has been requested
        if (
            self.layer.multiscale
            and self.layer.dims.ndisplay == 2
            and self.node.canvas is not None
        ):
            self.layer._update_multiscale(
                corner_pixels=old_corner_pixels,
                shape_threshold=self.node.canvas.size,
            )