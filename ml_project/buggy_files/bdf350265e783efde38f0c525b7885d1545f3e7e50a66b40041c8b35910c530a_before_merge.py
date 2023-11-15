    def run(self, workspace):
        first_image_set = workspace.measurements.get_current_image_measurement(
                cpmeas.GROUP_INDEX) == 1
        image_set_list = workspace.image_set_list
        d = self.get_dictionary(image_set_list)
        orig_image = workspace.image_set.get_image(self.image_name.value)
        recalculate_flag = (self.shape not in (SH_ELLIPSE, SH_RECTANGLE) or
                            self.individual_or_once == IO_INDIVIDUALLY or
                            first_image_set or
                            workspace.pipeline.test_mode)
        save_flag = (self.individual_or_once == IO_FIRST and first_image_set)
        if not recalculate_flag:
            if d[D_FIRST_CROPPING].shape != orig_image.pixel_data.shape[:2]:
                recalculate_flag = True
                logger.warning("""Image, "%s", size changed from %s to %s during cycle %d, recalculating""",
                               self.image_name.value,
                               str(d[D_FIRST_CROPPING].shape),
                               str(orig_image.pixel_data.shape[:2]),
                               workspace.image_set.image_number)
        mask = None  # calculate the mask after cropping unless set below
        cropping = None
        masking_objects = None
        if not recalculate_flag:
            cropping = d[D_FIRST_CROPPING]
            mask = d[D_FIRST_CROPPING_MASK]
        elif self.shape == SH_CROPPING:
            cropping_image = workspace.image_set.get_image(self.cropping_mask_source.value)
            cropping = cropping_image.crop_mask
        elif self.shape == SH_IMAGE:
            source_image = workspace.image_set.get_image \
                (self.image_mask_source.value).pixel_data

            cropping = source_image > 0
        elif self.shape == SH_OBJECTS:
            masking_objects = workspace.get_objects(self.objects_source.value)
            cropping = masking_objects.segmented > 0
        elif self.crop_method == CM_MOUSE:
            cropping = self.ui_crop(workspace, orig_image)
        elif self.shape == SH_ELLIPSE:
            cropping = self.get_ellipse_cropping(workspace, orig_image)
        elif self.shape == SH_RECTANGLE:
            cropping = self.get_rectangle_cropping(workspace, orig_image)
        if self.remove_rows_and_columns == RM_NO:
            cropped_pixel_data = orig_image.pixel_data.copy()
            if cropped_pixel_data.ndim == 3:
                cropped_pixel_data[~cropping, :] = 0
            else:
                cropped_pixel_data[np.logical_not(cropping)] = 0
            if mask is None:
                mask = cropping
            if orig_image.has_mask:
                image_mask = mask & orig_image.mask
            else:
                image_mask = mask
        else:
            internal_cropping = self.remove_rows_and_columns == RM_ALL
            cropped_pixel_data = cpi.crop_image(orig_image.pixel_data,
                                                cropping,
                                                internal_cropping)
            if mask is None:
                mask = cpi.crop_image(cropping, cropping, internal_cropping)
            if orig_image.has_mask:
                image_mask = cpi.crop_image(
                        orig_image.mask, cropping, internal_cropping) & mask
            else:
                image_mask = mask

            if cropped_pixel_data.ndim == 3:
                cropped_pixel_data[~mask, :] = 0
            else:
                cropped_pixel_data[~mask] = 0
        if self.shape == SH_OBJECTS:
            # Special handling for objects - masked objects instead of
            # mask and crop mask
            output_image = cpi.Image(image=cropped_pixel_data,
                                     masking_objects=masking_objects,
                                     parent_image=orig_image)
        else:
            output_image = cpi.Image(image=cropped_pixel_data,
                                     mask=image_mask,
                                     parent_image=orig_image,
                                     crop_mask=cropping)
        #
        # Display the image
        #
        if self.show_window:
            workspace.display_data.orig_image_pixel_data = orig_image.pixel_data
            workspace.display_data.cropped_pixel_data = cropped_pixel_data
            workspace.display_data.image_set_number = workspace.measurements.image_set_number

        if save_flag:
            d[D_FIRST_CROPPING_MASK] = mask
            d[D_FIRST_CROPPING] = cropping
        #
        # Save the image / cropping / mask
        #
        workspace.image_set.add(self.cropped_image_name.value, output_image)
        #
        # Save the old and new image sizes
        #
        original_image_area = np.product(orig_image.pixel_data.shape[:2])
        area_retained_after_cropping = np.sum(cropping)
        feature = FF_AREA_RETAINED % self.cropped_image_name.value
        m = workspace.measurements
        m.add_measurement('Image', feature,
                          np.array([area_retained_after_cropping]))
        feature = FF_ORIGINAL_AREA % self.cropped_image_name.value
        m.add_measurement('Image', feature,
                          np.array([original_image_area]))