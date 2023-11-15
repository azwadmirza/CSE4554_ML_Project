    def apply_ellipse_cropping(self, workspace, orig_image):
        d = self.get_dictionary(workspace.image_set_list)
        ellipse = d[SH_ELLIPSE]
        x_center, y_center, x_radius, y_radius = [
            ellipse[x] for x in (EL_XCENTER, EL_YCENTER, EL_XRADIUS, EL_YRADIUS)]
        pixel_data = orig_image.pixel_data
        x_max = pixel_data.shape[1]
        y_max = pixel_data.shape[0]
        if x_radius > y_radius:
            dist_x = math.sqrt(x_radius ** 2 - y_radius ** 2)
            dist_y = 0
            major_radius = x_radius
        else:
            dist_x = 0
            dist_y = math.sqrt(y_radius ** 2 - x_radius ** 2)
            major_radius = y_radius

        focus_1_x, focus_1_y = (x_center - dist_x, y_center - dist_y)
        focus_2_x, focus_2_y = (x_center + dist_x, y_center + dist_y)
        y, x = numpy.mgrid[0:y_max, 0:x_max]
        d1 = numpy.sqrt((x - focus_1_x) ** 2 + (y - focus_1_y) ** 2)
        d2 = numpy.sqrt((x - focus_2_x) ** 2 + (y - focus_2_y) ** 2)
        cropping = d1 + d2 <= major_radius * 2
        return cropping