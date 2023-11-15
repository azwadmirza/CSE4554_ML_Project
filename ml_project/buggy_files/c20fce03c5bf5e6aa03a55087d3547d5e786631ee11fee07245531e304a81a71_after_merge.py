    def apply_resize(self, workspace, input_image_name, output_image_name):
        image = workspace.image_set.get_image(input_image_name)
        image_pixels = image.pixel_data
        if self.size_method == R_BY_FACTOR:
            factor = self.resizing_factor.value
            shape = (np.array(image_pixels.shape[:2])*factor+.5).astype(int)
        elif self.size_method == R_TO_SIZE:
            if self.use_manual_or_image == C_MANUAL:
                shape = np.array([self.specific_height.value,
                                  self.specific_width.value])
            elif self.use_manual_or_image == C_IMAGE:
                shape = np.array(workspace.image_set.get_image(
                    self.specific_image.value).pixel_data.shape).astype(int)
            factor = np.array(shape, float) /np.array(image_pixels.shape, float)
        #
        # Little bit of wierdness here. The input pixels are numbered 0 to
        # shape-1 and so are the output pixels. Therefore the affine transform
        # is the ratio of the two shapes-1
        #
        ratio = ((np.array(image_pixels.shape[:2]).astype(float)-1) /
                 (shape.astype(float)-1))
        transform = np.array([[ratio[0], 0],[0,ratio[1]]])
        if self.interpolation not in I_ALL:
            raise NotImplementedError("Unsupported interpolation method: %s" %
                                      self.interpolation.value)
        order = (0 if self.interpolation == I_NEAREST_NEIGHBOR
                 else 1 if self.interpolation == I_BILINEAR
                 else 2)
        if image_pixels.ndim == 3:
            output_pixels = np.zeros((shape[0],shape[1],image_pixels.shape[2]), 
                                     image_pixels.dtype)
            for i in range(image_pixels.shape[2]):
                affine_transform(image_pixels[:,:,i], transform,
                                 output_shape = tuple(shape),
                                 output = output_pixels[:,:,i],
                                 order = order)
        else:
            output_pixels = affine_transform(image_pixels, transform,
                                             output_shape = shape,
                                             order = order)
        # Explicitly provide a mask in order to divorce our mask from
        # any that might be supplied by the parent.
        mask = affine_transform(image.mask.astype(float), transform,
                                output_shape = shape[:2],
                                order = 1) >= .5
        if image.has_crop_mask:
            input_cropping = image.crop_mask
            cropping_shape = (
                np.array(input_cropping.shape, float) * factor + .5).astype(int)
            eps = np.array([.50001, .50001]) / factor
            i = np.linspace(eps[0], input_cropping.shape[0]+eps[0], 
                            cropping_shape[0],
                            endpoint=False)
            j = np.linspace(eps[1], input_cropping.shape[1]+eps[1],
                            cropping_shape[1],
                            endpoint=False)
            ii, jj = np.mgrid[0:cropping_shape[0], 0:cropping_shape[1]]
            cropping = map_coordinates(
                input_cropping.astype(float),
                coordinates = [i[ii], j[jj]],
                order = 1, mode='nearest') >= .5
        else:
            cropping = mask
        output_image = cpi.Image(output_pixels, parent_image=image,
                                 mask=mask, crop_mask=cropping)
        workspace.image_set.add(output_image_name, output_image)

        if self.show_window:
            if not hasattr(workspace.display_data, 'input_images'):
                workspace.display_data.input_images = [image.pixel_data]
                workspace.display_data.output_images = [output_image.pixel_data]
                workspace.display_data.input_image_names = [input_image_name]
                workspace.display_data.output_image_names = [output_image_name]
            else:
                workspace.display_data.input_images += [image.pixel_data]
                workspace.display_data.output_images += [output_image.pixel_data]
                workspace.display_data.input_image_names += [input_image_name]
                workspace.display_data.output_image_names += [output_image_name]