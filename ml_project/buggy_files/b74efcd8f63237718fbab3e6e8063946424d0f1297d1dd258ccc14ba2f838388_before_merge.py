    def enhance_dark_holes(self, image, min_radius, max_radius):
        pixel_data = image.pixel_data

        mask = image.mask if image.has_mask else None

        se = self.__structuring_element(1, image.volumetric)

        inverted_image = pixel_data.max() - pixel_data

        previous_reconstructed_image = inverted_image

        eroded_image = inverted_image

        smoothed_image = numpy.zeros(pixel_data.shape)

        for i in range(max_radius + 1):
            eroded_image = skimage.morphology.erosion(eroded_image, se)

            if mask:
                eroded_image *= mask

            reconstructed_image = skimage.morphology.reconstruction(eroded_image, inverted_image, "dilation", se)

            output_image = previous_reconstructed_image - reconstructed_image

            if i >= min_radius:
                smoothed_image = numpy.maximum(smoothed_image, output_image)

            previous_reconstructed_image = reconstructed_image

        return smoothed_image