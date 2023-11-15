    def apply_alignment(self, workspace, input_image_name, output_image_name,
                        off_x, off_y, shape):
        '''Apply an alignment to the input image to result in the output image
        
        workspace - image set's workspace passed to run
        
        input_image_name - name of the image to be aligned
        
        output_image_name - name of the resultant image
        
        off_x, off_y - offset of the resultant image relative to the origninal
        
        shape - shape of the resultant image
        '''
        
        image = workspace.image_set.get_image(input_image_name,
                                              must_be_grayscale = True)
        output_pixels = np.zeros(shape)
        #
        # Copy the input to the output
        #
        p1, p2 = offset_slice(image.pixel_data, output_pixels, off_y, off_x)
        p2[:,:] = p1[:,:]
        output_mask = np.zeros(shape, bool)
        p1, p2 = offset_slice(image.mask, output_mask, off_y, off_x)
        p2[:,:] = p1[:,:]
        if np.all(output_mask):
            output_mask = None
        crop_mask = np.zeros(image.pixel_data.shape, bool)
        p1, p2 = offset_slice(crop_mask, output_pixels, off_y, off_x)
        p1[:,:] = True
        if np.all(crop_mask):
            crop_mask = None
        output_image = cpi.Image(output_pixels, 
                                 mask = output_mask, 
                                 crop_mask = crop_mask,
                                 parent_image = image)
        workspace.image_set.add(output_image_name, output_image)