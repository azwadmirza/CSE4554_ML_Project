    def get_threshold(self, image, mask, workspace):
        '''Calculate a local and global threshold
        
        img - base the threshold on this image's intensity
        
        mask - use this mask to define the pixels of interest
        
        workspace - get objects and measurements from this workspace and
                    add threshold measurements to this workspace's measurements.
        '''
        if self.threshold_scope == TM_MANUAL:
            local_threshold = global_threshold = self.manual_threshold.value
        else:
            if self.threshold_scope == TM_MEASUREMENT:
                m = workspace.measurements
                # Thresholds are stored as single element arrays.  Cast to
                # float to extract the value.
                value = float(m.get_current_image_measurement(
                    self.thresholding_measurement.value))
                value *= self.threshold_correction_factor.value
                if not self.threshold_range.min is None:
                    value = max(value, self.threshold_range.min)
                if not self.threshold_range.max is None:
                    value = min(value, self.threshold_range.max)
                local_threshold = global_threshold = value
            else:
                img = image.pixel_data
                if self.threshold_scope == TS_PER_OBJECT:
                    if self.masking_objects == O_FROM_IMAGE:
                        masking_objects = image.masking_objects
                    else:
                        masking_objects = workspace.object_set.get_objects(
                            self.masking_objects.value)
                    if masking_objects is not None:
                        label_planes = masking_objects.get_labels(img.shape[:2])
                    else:
                        label_planes = [image.mask.astype(int)]
                    if len(label_planes) == 1:
                        labels = label_planes[0][0]
                    else:
                        # For overlaps, we arbitrarily assign a pixel to
                        # the first label it appears in. Alternate would be
                        # to average, seems like it's too fine a point
                        # to deal with it. A third possibility would be to 
                        # treat overlaps as distinct entities since the overlapping
                        # areas will likely be different than either object.
                        labels = np.zeros(label_planes[0][0].shape,
                                          label_planes[0][0].dtype)
                        for label_plane, indices in label_planes:
                            labels[labels == 0] = label_plane[labels == 0]
                else:
                    labels = None
                if self.threshold_scope == TS_ADAPTIVE:
                    if self.adaptive_window_method == FI_IMAGE_SIZE:
                         # The original behavior
                        image_size = np.array(img.shape[:2], dtype=int)
                        block_size = image_size / 10
                        block_size[block_size<50] = 50
                    elif self.adaptive_window_method == FI_CUSTOM:
                        block_size = self.adaptive_window_size.value * \
                            np.array([1,1])
                else:
                    block_size = None
                object_fraction = self.object_fraction.value
                if object_fraction.endswith("%"):
                    object_fraction = float(object_fraction[:-1])/100.0
                else:
                    object_fraction = float(object_fraction)
                if self.threshold_scope == TS_AUTOMATIC:
                    threshold_range_min = 0
                    threshold_range_max = 1
                    threshold_correction_factor = 1
                else:
                    threshold_range_min = self.threshold_range.min
                    threshold_range_max = self.threshold_range.max
                    threshold_correction_factor = self.threshold_correction_factor.value
                local_threshold, global_threshold = get_threshold(
                    self.threshold_algorithm,
                    self.threshold_modifier,
                    img, 
                    mask = mask,
                    labels = labels,
                    threshold_range_min = threshold_range_min,
                    threshold_range_max = threshold_range_max,
                    threshold_correction_factor = threshold_correction_factor,
                    object_fraction = object_fraction,
                    two_class_otsu = self.two_class_otsu.value == O_TWO_CLASS,
                    use_weighted_variance = self.use_weighted_variance.value == O_WEIGHTED_VARIANCE,
                    assign_middle_to_foreground = self.assign_middle_to_foreground.value == O_FOREGROUND,
                    adaptive_window_size = block_size)
        self.add_threshold_measurements(workspace.measurements,
                                        local_threshold, global_threshold)
        if hasattr(workspace.display_data, "statistics"):
            workspace.display_data.statistics.append(
                ["Threshold","%0.3f"%(global_threshold)])
            
        return local_threshold, global_threshold