    def apply_rectangle_cropping(self, workspace, orig_image):
        cropping = numpy.ones(orig_image.pixel_data.shape[:2], bool)
        d = self.get_dictionary(workspace.image_set_list)
        r = d[SH_RECTANGLE]
        left, top, right, bottom = [
            int(numpy.round(r[x])) for x in (RE_LEFT, RE_TOP, RE_RIGHT, RE_BOTTOM)]
        if left > 0:
            cropping[:, :left] = False
        if right < cropping.shape[1]:
            cropping[:, right:] = False
        if top > 0:
            cropping[:top, :] = False
        if bottom < cropping.shape[0]:
            cropping[bottom:, :] = False
        return cropping