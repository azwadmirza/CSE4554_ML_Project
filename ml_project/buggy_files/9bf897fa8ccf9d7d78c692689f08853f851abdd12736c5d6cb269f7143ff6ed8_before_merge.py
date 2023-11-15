    def post_group(self, workspace, grouping):
        image_set = workspace.image_set
        if self.output_image.value not in image_set.get_names():
            d = self.get_dictionary(workspace.image_set_list)
            image_set.add(self.output_image.value, 
                          cpi.Image(d[TILED_IMAGE]))