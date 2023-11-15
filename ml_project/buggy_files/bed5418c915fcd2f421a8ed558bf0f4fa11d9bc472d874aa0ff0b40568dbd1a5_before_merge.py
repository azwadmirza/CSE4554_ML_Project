    def scale_axes(self):
        """Set the axes limits appropriate to the images we have"""
        ax = self.image.axes
        if self.frame.navtoolbar.is_home():
            max_x = max_y = 0
            for image_row in self.image_rows:
                if image_row.data.mode != MODE_HIDE:
                    shape = image_row.data.pixel_data.shape
                    max_x = max(shape[1], max_x)
                    max_y = max(shape[0], max_y)
            if max_x > 0 and max_y > 0:
                max_x -= 0.5
                max_y -= 0.5
                ax.set_xlim(-0.5, max_x)
                ax.set_ylim(-0.5, max_y)
                ax.invert_yaxis()
                self.__axes_scale = (max_y, max_x)
                self.frame.navtoolbar.reset()