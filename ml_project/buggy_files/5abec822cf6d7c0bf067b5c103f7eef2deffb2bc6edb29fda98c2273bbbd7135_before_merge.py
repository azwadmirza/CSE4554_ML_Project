    def resized_shape(self, image, workspace):
        image_pixels = image.pixel_data

        shape = numpy.array(image_pixels.shape).astype(numpy.float)

        if self.size_method.value == R_BY_FACTOR:
            factor = self.resizing_factor.value

            if image.volumetric:
                height, width = shape[1:3]
            else:
                height, width = shape[:2]

            height *= factor

            width *= factor
        else:
            if self.use_manual_or_image.value == C_MANUAL:
                height = self.specific_height.value
                width = self.specific_width.value
            else:
                other_image = workspace.image_set.get_image(self.specific_image.value)

                if image.volumetric:
                    height, width = other_image.pixel_data.shape[1:3]
                else:
                    height, width = other_image.pixel_data.shape[:2]

        new_shape = []

        if image.volumetric:
            new_shape += [shape[0]]

        new_shape += [height, width]

        if image.multichannel:
            new_shape += [shape[-1]]

        return numpy.asarray(new_shape)