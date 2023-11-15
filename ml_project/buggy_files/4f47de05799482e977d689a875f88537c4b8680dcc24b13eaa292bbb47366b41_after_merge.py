    def threshold_image(self, image_name, workspace, 
                        wants_local_threshold=False):
        """Compute the threshold using whichever algorithm was selected by the user
        
        image_name - name of the image to use for thresholding
        
        workspace - get any measurements / objects / images from the workspace
        
        returns: thresholded binary image
        """
        #
        # Retrieve the relevant image and mask
        #
        image = workspace.image_set.get_image(image_name,
                                              must_be_grayscale = True)
        img = image.pixel_data
        mask = image.mask
        if self.threshold_scope == TS_BINARY_IMAGE:
            binary_image = workspace.image_set.get_image(
                self.binary_image.value, must_be_binary = True).pixel_data
            self.add_fg_bg_measurements(
                workspace.measurements, img, mask, binary_image)
            if wants_local_threshold:
                return binary_image, None
            return binary_image
        local_threshold, global_threshold = self.get_threshold(
            image, mask, workspace)
    
        if self.threshold_smoothing_choice == TSM_NONE:
            blurred_image = img
            sigma = 0
        else:
            if self.threshold_smoothing_choice == TSM_AUTOMATIC:
                sigma = 1
            else:
                # Convert from a scale into a sigma. What I've done here
                # is to structure the Gaussian so that 1/2 of the smoothed
                # intensity is contributed from within the smoothing diameter
                # and 1/2 is contributed from outside.
                sigma = self.threshold_smoothing_scale.value / 0.6744 / 2.0
            def fn(img, sigma=sigma):
                return scipy.ndimage.gaussian_filter(
                    img, sigma, mode='constant', cval=0)
            blurred_image = smooth_with_function_and_mask(img, fn, mask)
        if hasattr(workspace,"display_data"):
            workspace.display_data.threshold_sigma = sigma          
            
        binary_image = (blurred_image >= local_threshold) & mask
        self.add_fg_bg_measurements(
            workspace.measurements, img, mask, binary_image)
        if wants_local_threshold:
            return binary_image, local_threshold
        return binary_image