    def align(self, workspace, input1_name, input2_name):
        '''Align the second image with the first
        
        Calculate the alignment offset that must be added to indexes in the
        first image to arrive at indexes in the second image.
        
        Returns the x,y (not i,j) offsets.
        '''
        image1 = workspace.image_set.get_image(input1_name,
                                               must_be_grayscale=True)
        image1_pixels = image1.pixel_data
        image2 = workspace.image_set.get_image(input2_name,
                                               must_be_grayscale=True)
        image2_pixels = image2.pixel_data
        if self.alignment_method == M_CROSS_CORRELATION:
            return self.align_cross_correlation(image1_pixels, image2_pixels)
        else:
            image1_mask = image1.mask
            image2_mask = image2.mask
            return self.align_mutual_information(image1_pixels, image2_pixels,
                                                 image1_mask, image2_mask)