    def rehint(self):
        height, width = self._resize_max(
            original_height=self._pixbuf.get_height(),
            original_width=self._pixbuf.get_width(),
            max_height=self.native.get_allocated_height(),
            max_width=self.native.get_allocated_width()
        )

        scaled_pixbuf = self._pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
        self._image.set_from_pixbuf(scaled_pixbuf)