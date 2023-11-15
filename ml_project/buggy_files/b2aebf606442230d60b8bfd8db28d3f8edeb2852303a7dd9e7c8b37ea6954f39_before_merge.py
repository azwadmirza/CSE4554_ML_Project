    def align_mutual_information(self, pixels1, pixels2, mask1, mask2):
        '''Align the second image with the first using mutual information
        
        returns the x,y offsets to add to image1's indexes to align it with
        image2
        
        The algorithm computes the mutual information content of the two
        images, offset by one in each direction (including diagonal) and
        then picks the direction in which there is the most mutual information.
        From there, it tries all offsets again and so on until it reaches
        a local maximum.
        '''
        def mutualinf(x, y, maskx, masky):
            x = x[maskx & masky]
            y = y[maskx & masky]
            return entropy(x) + entropy(y) - entropy2(x,y)
        
        maxshape = np.maximum(pixels1.shape, pixels2.shape)
        pixels1 = reshape_image(pixels1, maxshape)
        pixels2 = reshape_image(pixels2, maxshape)
        mask1 = reshape_image(mask1, maxshape)
        mask2 = reshape_image(mask2, maxshape)
            
        best = mutualinf(pixels1, pixels2, mask1, mask2)
        i = 0
        j = 0
        while True:
            last_i = i
            last_j = j
            for new_i in range(last_i-1,last_i+2):
                for new_j in range(last_j-1, last_j+2):
                    if new_i == 0 and new_j == 0:
                        continue
                    p2, p1 = offset_slice(pixels2,pixels1, new_i, new_j)
                    m2, m1 = offset_slice(mask2, mask1, new_i, new_j)
                    info = mutualinf(p1, p2, m1, m2)
                    if info > best:
                        best = info
                        i = new_i
                        j = new_j
            if i == last_i and j == last_j:
                return j,i