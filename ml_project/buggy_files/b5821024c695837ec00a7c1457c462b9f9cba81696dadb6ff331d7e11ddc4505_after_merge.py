    def run(self, workspace):
        image_names = [image.image_name.value for image in self.images if image.image_or_measurement == IM_IMAGE]
        image_factors = [image.factor.value for image in self.images]
        wants_image = [image.image_or_measurement == IM_IMAGE for image in self.images]

        if self.operation.value in [O_INVERT, O_LOG_TRANSFORM, O_LOG_TRANSFORM_LEGACY, O_NOT, O_NONE]:
            # these only operate on the first image
            image_names = image_names[:1]
            image_factors = image_factors[:1]

        images = [workspace.image_set.get_image(x) for x in image_names]
        pixel_data = [image.pixel_data for image in images]
        masks = [image.mask if image.has_mask else None for image in images]

        # Crop all of the images similarly
        smallest = numpy.argmin([numpy.product(pd.shape) for pd in pixel_data])
        smallest_image = images[smallest]
        for i in [x for x in range(len(images)) if x != smallest]:
            pixel_data[i] = smallest_image.crop_image_similarly(pixel_data[i])
            if masks[i] is not None:
                masks[i] = smallest_image.crop_image_similarly(masks[i])

        # weave in the measurements
        idx = 0
        measurements = workspace.measurements
        for i in range(self.operand_count):
            if not wants_image[i]:
                value = measurements.get_current_image_measurement(self.images[i].measurement.value)
                value = numpy.NaN if value is None else float(value)
                pixel_data.insert(i, value)
                masks.insert(i, True)

        # Multiply images by their factors
        for i, image_factor in enumerate(image_factors):
            if image_factor != 1 and self.operation not in BINARY_OUTPUT_OPS:
                pixel_data[i] = pixel_data[i] * image_factors[i]

        output_pixel_data = pixel_data[0]
        output_mask = masks[0]

        opval = self.operation.value
        if opval in [O_ADD, O_SUBTRACT, O_DIFFERENCE, O_MULTIPLY, O_DIVIDE,
                     O_AVERAGE, O_MAXIMUM, O_MINIMUM, O_AND, O_OR, O_EQUALS]:
            # Binary operations
            if opval in (O_ADD, O_AVERAGE):
                op = numpy.add
            elif opval == O_SUBTRACT:
                if self.use_logical_operation(pixel_data):
                    op = numpy.logical_xor
                else:
                    op = numpy.subtract
            elif opval == O_DIFFERENCE:
                if self.use_logical_operation(pixel_data):
                    op = numpy.logical_xor
                else:
                    def op(x, y):
                        return numpy.abs(numpy.subtract(x, y))
            elif opval == O_MULTIPLY:
                if self.use_logical_operation(pixel_data):
                    op = numpy.logical_and
                else:
                    op = numpy.multiply
            elif opval == O_MINIMUM:
                op = numpy.minimum
            elif opval == O_MAXIMUM:
                op = numpy.maximum
            elif opval == O_AND:
                op = numpy.logical_and
            elif opval == O_OR:
                op = numpy.logical_or
            elif opval == O_EQUALS:
                output_pixel_data = numpy.ones(pixel_data[0].shape, bool)
                comparitor = pixel_data[0]
            else:
                op = numpy.divide
            for pd, mask in zip(pixel_data[1:], masks[1:]):
                if not numpy.isscalar(pd) and output_pixel_data.ndim != pd.ndim:
                    if output_pixel_data.ndim == 2:
                        output_pixel_data = output_pixel_data[:, :, numpy.newaxis]
                        if opval == O_EQUALS and not numpy.isscalar(comparitor):
                            comparitor = comparitor[:, :, numpy.newaxis]
                    if pd.ndim == 2:
                        pd = pd[:, :, numpy.newaxis]
                if opval == O_EQUALS:
                    output_pixel_data = output_pixel_data & (comparitor == pd)
                else:
                    output_pixel_data = op(output_pixel_data, pd)
                if self.ignore_mask:
                    continue
                else:
                    if output_mask is None:
                        output_mask = mask
                    elif mask is not None:
                        output_mask = (output_mask & mask)
            if opval == O_AVERAGE:
                if not self.use_logical_operation(pixel_data):
                    output_pixel_data /= sum(image_factors)
        elif opval == O_INVERT:
            output_pixel_data = skimage.util.invert(output_pixel_data)
        elif opval == O_NOT:
            output_pixel_data = numpy.logical_not(output_pixel_data)
        elif opval == O_LOG_TRANSFORM:
            output_pixel_data = numpy.log2(output_pixel_data + 1)
        elif opval == O_LOG_TRANSFORM_LEGACY:
            output_pixel_data = numpy.log2(output_pixel_data)
        elif opval == O_NONE:
            output_pixel_data = output_pixel_data.copy()
        else:
            raise NotImplementedError("The operation %s has not been implemented" % opval)

        # Check to see if there was a measurement & image w/o mask. If so
        # set mask to none
        if numpy.isscalar(output_mask):
            output_mask = None
        if opval not in BINARY_OUTPUT_OPS:
            #
            # Post-processing: exponent, multiply, add
            #
            if self.exponent.value != 1:
                output_pixel_data **= self.exponent.value
            if self.after_factor.value != 1:
                output_pixel_data *= self.after_factor.value
            if self.addend.value != 0:
                output_pixel_data += self.addend.value

            #
            # truncate values
            #
            if self.truncate_low.value:
                output_pixel_data[output_pixel_data < 0] = 0
            if self.truncate_high.value:
                output_pixel_data[output_pixel_data > 1] = 1

        #
        # add the output image to the workspace
        #
        crop_mask = (smallest_image.crop_mask
                     if smallest_image.has_crop_mask else None)
        masking_objects = (smallest_image.masking_objects
                           if smallest_image.has_masking_objects else None)
        output_image = cellprofiler.image.Image(output_pixel_data,
                                                mask=output_mask,
                                                crop_mask=crop_mask,
                                                parent_image=images[0],
                                                masking_objects=masking_objects,
                                                convert=False,
                                                dimensions=images[0].dimensions)
        workspace.image_set.add(self.output_image_name.value, output_image)

        #
        # Display results
        #
        if self.show_window:
            workspace.display_data.pixel_data = [image.pixel_data for image in images] + [output_pixel_data]

            workspace.display_data.display_names = image_names + [self.output_image_name.value]

            workspace.display_data.dimensions = output_image.dimensions