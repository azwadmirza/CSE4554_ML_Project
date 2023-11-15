    def run_bw(self, workspace):
        image_set = workspace.image_set
        if self.blank_image.value:
            outline_image = image_set.get_image(
                self.outlines[0].outline_name.value,
                must_be_binary = True)
            mask = outline_image.pixel_data
            pixel_data = np.zeros((mask.shape))
            maximum = 1
        else:
            image = image_set.get_image(self.image_name.value,
                                        must_be_grayscale=True)
            pixel_data = image.pixel_data
            maximum = 1 if self.max_type == MAX_POSSIBLE else np.max(pixel_data)
            pixel_data = pixel_data.copy()
        for outline in self.outlines:
            mask = self.get_outline(workspace, outline)
            i_max = min(mask.shape[0], pixel_data.shape[0])
            j_max = min(mask.shape[1], pixel_data.shape[1])
            mask = mask[:i_max, :j_max]
            pixel_data[:i_max, :j_max][mask] = maximum
        return pixel_data