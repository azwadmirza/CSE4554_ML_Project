    def align_cross_correlation(self, pixels1, pixels2):
        '''Align the second image with the first using max cross-correlation
        
        returns the x,y offsets to add to image1's indexes to align it with
        image2
        
        Many of the ideas here are based on the paper, "Fast Normalized
        Cross-Correlation" by J.P. Lewis 
        (http://www.idiom.com/~zilla/Papers/nvisionInterface/nip.html)
        which is frequently cited when addressing this problem.
        '''
        #
        # TODO: Possibly use all 3 dimensions for color some day
        #
        if pixels1.ndim == 3:
            pixels1 = np.mean(pixels1, 2)
        if pixels2.ndim == 3:
            pixels2 = np.mean(pixels2, 2)
        #
        # We double the size of the image to get a field of zeros
        # for the parts of one image that don't overlap the displaced
        # second image.
        #
        # Since we're going into the frequency domain, if the images are of
        # different sizes, we can make the FFT shape large enough to capture
        # the period of the largest image - the smaller just will have zero
        # amplitude at that frequency.
        #
        s = np.maximum(pixels1.shape, pixels2.shape)
        fshape = s*2
        #
        # Calculate the # of pixels at a particular point
        #
        i,j = np.mgrid[-s[0]:s[0],
                       -s[1]:s[1]]
        unit = np.abs(i*j).astype(float)
        unit[unit<1]=1 # keeps from dividing by zero in some places
        #
        # Normalize the pixel values around zero which does not affect the
        # correlation, keeps some of the sums of multiplications from
        # losing precision and precomputes t(x-u,y-v) - t_mean
        #
        pixels1 = pixels1-np.mean(pixels1)
        pixels2 = pixels2-np.mean(pixels2)
        #
        # Lewis uses an image, f and a template t. He derives a normalized
        # cross correlation, ncc(u,v) =
        # sum((f(x,y)-f_mean(u,v))*(t(x-u,y-v)-t_mean),x,y) /
        # sqrt(sum((f(x,y)-f_mean(u,v))**2,x,y) * (sum((t(x-u,y-v)-t_mean)**2,x,y)
        #
        # From here, he finds that the numerator term, f_mean(u,v)*(t...) is zero
        # leaving f(x,y)*(t(x-u,y-v)-t_mean) which is a convolution of f
        # by t-t_mean.
        #
        fp1 = fft2(pixels1,fshape)
        fp2 = fft2(pixels2,fshape)
        corr12 = ifft2(fp1 * fp2.conj()).real
        
        #
        # Use the trick of Lewis here - compute the cumulative sums
        # in a fashion that accounts for the parts that are off the
        # edge of the template.
        #
        # We do this in quadrants:
        # q0 q1
        # q2 q3
        # For the first, 
        # q0 is the sum over pixels1[i:,j:] - sum i,j backwards
        # q1 is the sum over pixels1[i:,:j] - sum i backwards, j forwards
        # q2 is the sum over pixels1[:i,j:] - sum i forwards, j backwards
        # q3 is the sum over pixels1[:i,:j] - sum i,j forwards
        #
        # The second is done as above but reflected lr and ud
        #
        p1_si = pixels1.shape[0]
        p1_sj = pixels1.shape[1]
        p1_sum = np.zeros(fshape)
        p1_sum[:p1_si,:p1_sj] = cumsum_quadrant(pixels1, False, False)
        p1_sum[:p1_si,-p1_sj:] = cumsum_quadrant(pixels1, False, True)
        p1_sum[-p1_si:,:p1_sj] = cumsum_quadrant(pixels1, True, False)
        p1_sum[-p1_si:,-p1_sj:] = cumsum_quadrant(pixels1, True, True)
        #
        # Divide the sum over the # of elements summed-over
        #
        p1_mean = p1_sum / unit
        
        p2_si = pixels2.shape[0]
        p2_sj = pixels2.shape[1]
        p2_sum = np.zeros(fshape)
        p2_sum[:p2_si,:p2_sj] = cumsum_quadrant(pixels2, False, False)
        p2_sum[:p2_si,-p2_sj:] = cumsum_quadrant(pixels2, False, True)
        p2_sum[-p2_si:,:p2_sj] = cumsum_quadrant(pixels2, True, False)
        p2_sum[-p2_si:,-p2_sj:] = cumsum_quadrant(pixels2, True, True)
        p2_sum = np.fliplr(np.flipud(p2_sum))
        p2_mean = p2_sum / unit
        #
        # Once we have the means for u,v, we can caluclate the
        # variance-like parts of the equation. We have to multiply
        # the mean^2 by the # of elements being summed-over
        # to account for the mean being summed that many times.
        #
        p1sd = np.sum(pixels1**2) - p1_mean**2 * np.product(s)
        p2sd = np.sum(pixels2**2) - p2_mean**2 * np.product(s)
        #
        # There's always chance of roundoff error for a zero value
        # resulting in a negative sd, so limit the sds here
        #
        sd = np.sqrt(np.maximum(p1sd * p2sd, 0))
        corrnorm = corr12 / sd
        #
        # There's not much information for points where the standard
        # deviation is less than 1/100 of the maximum. We exclude these
        # from consideration.
        # 
        corrnorm[(unit < np.product(s) / 2) &
                 (sd < np.mean(sd) / 100)] = 0
        i,j = np.unravel_index(np.argmax(corrnorm ),fshape)
        #
        # Reflect values that fall into the second half
        #
        if i > pixels1.shape[0]:
            i = i - fshape[0]
        if j > pixels1.shape[1]:
            j = j - fshape[1]
        return j,i