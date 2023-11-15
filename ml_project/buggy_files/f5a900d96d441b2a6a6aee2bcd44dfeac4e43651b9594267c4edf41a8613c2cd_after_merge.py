    def rehint(self):
        if self._pixbuf:
            height, width = self._resize_max(
                original_height=self._pixbuf.get_height(),
                original_width=self._pixbuf.get_width(),
                max_height=self.native.get_allocated_height(),
                max_width=self.native.get_allocated_width(),
            )

            dpr = self.native.get_scale_factor()

            scaled_pixbuf = self._pixbuf.scale_simple(
                width * dpr, height * dpr, GdkPixbuf.InterpType.BILINEAR
            )

            surface = Gdk.cairo_surface_create_from_pixbuf(
                scaled_pixbuf, 0, self.native.get_window()  # scale: 0 = same as window
            )
            self._image.set_from_surface(surface)