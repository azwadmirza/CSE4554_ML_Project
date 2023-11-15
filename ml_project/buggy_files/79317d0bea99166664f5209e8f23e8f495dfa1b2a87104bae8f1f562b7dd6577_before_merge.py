    def display(self, workspace, figure):
        input_image_names = workspace.display_data.input_image_names
        images = workspace.display_data.images
        nsubplots = len(input_image_names)

        if self.scheme_choice == SCHEME_CMYK:
            subplots = (3,2)
            subplot_indices = ((0,0),(0,1),(1,0),(1,1),(2,0))
            color_subplot = (2,1)
        elif self.scheme_choice == SCHEME_RGB:
            subplots = (2,2)
            subplot_indices = ((0,0),(0,1),(1,0))
            color_subplot = (1,1)
        else:
            subplots = (min(nsubplots+1,4), int(nsubplots/4) + 1)
            subplot_indices = [(i % 4, int(i / 4)) for i in range(nsubplots)]
            color_subplot = (nsubplots % 4, int(nsubplots / 4))
        figure.set_subplots(subplots)
        for i, (input_image_name, image_pixel_data) in \
                enumerate(zip(input_image_names, images)):
            x,y = subplot_indices[i]
            figure.subplot_imshow_grayscale(x, y, image_pixel_data,
                                              title=input_image_name,
                                              sharexy = figure.subplot(0,0))
            figure.subplot(x,y).set_visible(True)
        for x, y in subplot_indices[len(input_image_names):]:
            figure.subplot(x,y).set_visible(False)
        figure.subplot_imshow(color_subplot[0], color_subplot[1],
                                workspace.display_data.rgb_pixel_data,
                                title=self.rgb_image_name.value,
                                sharexy = figure.subplot(0,0))