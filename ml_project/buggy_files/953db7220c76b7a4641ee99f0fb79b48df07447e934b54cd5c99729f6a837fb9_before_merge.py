    def screenshot(self, region=None, size=None, bgcolor=None, crop=None):
        """Render the scene to an offscreen buffer and return the image array.

        Parameters
        ----------
        region : tuple | None
            Specifies the region of the canvas to render. Format is
            (x, y, w, h). By default, the entire canvas is rendered.
        size : tuple | None
            Specifies the size of the image array to return. If no size is
            given, then the size of the *region* is used, multiplied by the
            pixel scaling factor of the canvas (see `pixel_scale`). This
            argument allows the scene to be rendered at resolutions different
            from the native canvas resolution.
        bgcolor : instance of Color | None
            The background color to use.
        crop : array-like | None
            If specified it determines the pixels read from the framebuffer.
            In the format (x, y, w, h), relative to the region being rendered.
        Returns
        -------
        image : array
            Numpy array of type ubyte and shape (h, w, 4). Index [0, 0] is the
            upper-left corner of the rendered region.

        """
        return self._canvas.render(region=None, size=None, bgcolor=None,
                                   crop=None)