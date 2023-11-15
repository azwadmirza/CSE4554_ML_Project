    def apply_resize(self, workspace, input_image_name, output_image_name):
        image = workspace.image_set.get_image(input_image_name)

        image_pixels = image.pixel_data

        new_shape = self.resized_shape(image, workspace)

        order = self.spline_order()
        # Pixel values need to be between -1, 1 in order to use  skimage resize
        # Thus determine a factor to scale by
        img_scale_fac = numpy.abs(image_pixels).max()

        if image.volumetric and image.multichannel:
            output_pixels = numpy.zeros(new_shape.astype(int), dtype=image_pixels.dtype)


            for idx in range(int(new_shape[-1])):
                output_pixels[:, :, :, idx] = skimage.transform.resize(
                    image_pixels[:, :, :, idx]/img_scale_fac,
                    new_shape[:-1],
                    order=order,
                    mode="symmetric"
                )
        else:
            output_pixels = skimage.transform.resize(
                image_pixels/img_scale_fac,
                new_shape,
                order=order,
                mode="symmetric"
            )

        if image.multichannel and len(new_shape) > image.dimensions:
            new_shape = new_shape[:-1]

        if img_scale_fac != 1:
            # if the image intensities were scaled,
            # scale them back in the output
            output_pixels = output_pixels*img_scale_fac

        mask = skimage.transform.resize(
            image.mask,
            new_shape,
            order=0,
            mode="constant"
        )

        mask = skimage.img_as_bool(mask)

        if image.has_crop_mask:
            cropping = skimage.transform.resize(
                image.crop_mask,
                new_shape,
                order=0,
                mode="constant"
            )

            cropping = skimage.img_as_bool(cropping)
        else:
            cropping = None

        output_image = cellprofiler.image.Image(
            output_pixels,
            parent_image=image,
            mask=mask,
            crop_mask=cropping,
            dimensions=image.dimensions
        )

        workspace.image_set.add(output_image_name, output_image)

        if self.show_window:
            if hasattr(workspace.display_data, 'input_images'):
                workspace.display_data.multichannel += [image.multichannel]
                workspace.display_data.input_images += [image.pixel_data]
                workspace.display_data.output_images += [output_image.pixel_data]
                workspace.display_data.input_image_names += [input_image_name]
                workspace.display_data.output_image_names += [output_image_name]
            else:
                workspace.display_data.dimensions = image.dimensions
                workspace.display_data.multichannel = [image.multichannel]
                workspace.display_data.input_images = [image.pixel_data]
                workspace.display_data.output_images = [output_image.pixel_data]
                workspace.display_data.input_image_names = [input_image_name]
                workspace.display_data.output_image_names = [output_image_name]