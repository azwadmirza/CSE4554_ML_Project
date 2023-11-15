    def display_combine(self, workspace, figure):
        import matplotlib.cm

        input_image = workspace.display_data.input_image
        output_image = workspace.display_data.output_image
        figure.set_subplots((1, 2))
        figure.subplot_imshow(0, 0, input_image,
                              title="Original image: %s" % self.image_name)
        figure.subplot_imshow(0, 1, output_image,
                              title="Grayscale image: %s" % self.grayscale_name,
                              colormap=matplotlib.cm.Greys_r,
                              sharexy=figure.subplot(0, 0))