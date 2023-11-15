    def scale_axes(self):
        """Set the axes limits appropriate to the images we have"""
        max_x = max_y = 0
        for image_row in self.image_rows:
            if image_row.data.mode != MODE_HIDE:
                shape = image_row.data.pixel_data.shape
                max_x = max(shape[1], max_x)
                max_y = max(shape[0], max_y)
        if self.__axes_scale is not None:
            init_x, init_y = self.__axes_scale
            if float(max_x) != init_x[1] or float(max_y) != init_y[0]:
                self.__axes_scale = None
                self.frame.navtoolbar._nav_stack.clear()
            elif init_x != self.axes.get_xlim() or init_y != self.axes.get_ylim():
                return
        if max_x > 0 and max_y > 0:
            self.axes.set_xlim(0, max_x)
            self.axes.set_ylim(0, max_y)
            self.axes.invert_yaxis()
            self.__axes_scale = ((0.0, float(max_x)), (float(max_y), 0.0))
            self.frame.navtoolbar.reset()