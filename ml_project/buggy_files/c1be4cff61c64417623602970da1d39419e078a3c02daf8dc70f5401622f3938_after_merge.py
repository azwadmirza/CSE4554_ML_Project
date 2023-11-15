    def ui_crop(self, workspace, orig_image):
        """Crop into a rectangle or ellipse, guided by UI"""
        d = self.get_dictionary(workspace.image_set_list)
        if (self.shape.value not in d) or self.individual_or_once == IO_INDIVIDUALLY:
            d[self.shape.value] = \
                workspace.interaction_request(self, d.get(self.shape.value, None), orig_image.pixel_data)
        if self.shape == SH_ELLIPSE:
            return self.apply_ellipse_cropping(workspace, orig_image)
        else:
            return self.apply_rectangle_cropping(workspace, orig_image)