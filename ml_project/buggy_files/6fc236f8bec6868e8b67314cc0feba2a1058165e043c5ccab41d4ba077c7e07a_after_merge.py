    def run_image_pair_objects(self, workspace, first_image_name,
                               second_image_name, object_name):
        '''Calculate per-object correlations between intensities in two images'''
        first_image = workspace.image_set.get_image(first_image_name,
                                                    must_be_grayscale=True)
        second_image = workspace.image_set.get_image(second_image_name,
                                                     must_be_grayscale=True)
        objects = workspace.object_set.get_objects(object_name)
        #
        # Crop both images to the size of the labels matrix
        #
        labels = objects.segmented
        try:
            first_pixels = objects.crop_image_similarly(first_image.pixel_data)
            first_mask = objects.crop_image_similarly(first_image.mask)
        except ValueError:
            first_pixels, m1 = cpo.size_similarly(labels, first_image.pixel_data)
            first_mask, m1 = cpo.size_similarly(labels, first_image.mask)
            first_mask[~m1] = False
        try:
            second_pixels = objects.crop_image_similarly(second_image.pixel_data)
            second_mask = objects.crop_image_similarly(second_image.mask)
        except ValueError:
            second_pixels, m1 = cpo.size_similarly(labels, second_image.pixel_data)
            second_mask, m1 = cpo.size_similarly(labels, second_image.mask)
            second_mask[~m1] = False
        mask = ((labels > 0) & first_mask & second_mask)
        first_pixels = first_pixels[mask]
        second_pixels = second_pixels[mask]
        labels = labels[mask]
        result = []
        first_pixel_data = first_image.pixel_data
        first_mask = first_image.mask
        first_pixel_count = np.product(first_pixel_data.shape)
        second_pixel_data = second_image.pixel_data
        second_mask = second_image.mask
        second_pixel_count = np.product(second_pixel_data.shape)
        #
        # Crop the larger image similarly to the smaller one
        #
        if first_pixel_count < second_pixel_count:
            second_pixel_data = first_image.crop_image_similarly(second_pixel_data)
            second_mask = first_image.crop_image_similarly(second_mask)
        elif second_pixel_count < first_pixel_count:
            first_pixel_data = second_image.crop_image_similarly(first_pixel_data)
            first_mask = second_image.crop_image_similarly(first_mask)
        mask = (first_mask & second_mask &
                (~ np.isnan(first_pixel_data)) &
                (~ np.isnan(second_pixel_data)))
        if np.any(mask):
            #
            # Perform the correlation, which returns:
            # [ [ii, ij],
            #   [ji, jj] ]
            #
            fi = first_pixel_data[mask]
            si = second_pixel_data[mask]

        n_objects = objects.count
        # Handle case when both images for the correlation are completely masked out

        if n_objects == 0:
            corr = np.zeros((0,))
            overlap = np.zeros((0,))
            K1 = np.zeros((0,))
            K2 = np.zeros((0,))
            M1 = np.zeros((0,))
            M2 = np.zeros((0,))
            RWC1 = np.zeros((0,))
            RWC2 = np.zeros((0,))
            C1 = np.zeros((0,))
            C2 = np.zeros((0,))
        elif np.where(mask)[0].__len__() == 0:
            corr = np.zeros((n_objects,))
            corr[:] = np.NaN
            overlap = K1 = K2 = M1 = M2 = RWC1 = RWC2 = C1 = C2 = corr
        else:
            #
            # The correlation is sum((x-mean(x))(y-mean(y)) /
            #                         ((n-1) * std(x) *std(y)))
            #
            lrange = np.arange(n_objects, dtype=np.int32) + 1
            area = fix(scind.sum(np.ones_like(labels), labels, lrange))
            mean1 = fix(scind.mean(first_pixels, labels, lrange))
            mean2 = fix(scind.mean(second_pixels, labels, lrange))
            #
            # Calculate the standard deviation times the population.
            #
            std1 = np.sqrt(fix(scind.sum((first_pixels - mean1[labels - 1]) ** 2,
                                         labels, lrange)))
            std2 = np.sqrt(fix(scind.sum((second_pixels - mean2[labels - 1]) ** 2,
                                         labels, lrange)))
            x = first_pixels - mean1[labels - 1]  # x - mean(x)
            y = second_pixels - mean2[labels - 1]  # y - mean(y)
            corr = fix(scind.sum(x * y / (std1[labels - 1] * std2[labels - 1]),
                                 labels, lrange))
            # Explicitly set the correlation to NaN for masked objects
            corr[scind.sum(1, labels, lrange) == 0] = np.NaN
            result += [
                [first_image_name, second_image_name, object_name, "Mean Correlation coeff", "%.3f" % np.mean(corr)],
                [first_image_name, second_image_name, object_name, "Median Correlation coeff",
                 "%.3f" % np.median(corr)],
                [first_image_name, second_image_name, object_name, "Min Correlation coeff", "%.3f" % np.min(corr)],
                [first_image_name, second_image_name, object_name, "Max Correlation coeff", "%.3f" % np.max(corr)]]

            # Threshold as percentage of maximum intensity of objects in each channel
            tff = (self.thr.value / 100) * fix(scind.maximum(first_pixels, labels, lrange))
            tss = (self.thr.value / 100) * fix(scind.maximum(second_pixels, labels, lrange))

            combined_thresh = (first_pixels >= tff[labels - 1]) & (second_pixels >= tss[labels - 1])
            fi_thresh = first_pixels[combined_thresh]
            si_thresh = second_pixels[combined_thresh]
            tot_fi_thr = scind.sum(first_pixels[first_pixels >= tff[labels - 1]], labels[first_pixels >= tff[labels - 1]],
                                   lrange)
            tot_si_thr = scind.sum(second_pixels[second_pixels >= tss[labels - 1]],
                                   labels[second_pixels >= tss[labels - 1]], lrange)

            nonZero = (fi > 0) | (si > 0)
            xvar = np.var(fi[nonZero], axis=0, ddof=1)
            yvar = np.var(si[nonZero], axis=0, ddof=1)

            xmean = np.mean(fi[nonZero], axis=0)
            ymean = np.mean(si[nonZero], axis=0)

            z = fi[nonZero] + si[nonZero]
            zvar = np.var(z, axis=0, ddof=1)

            covar = 0.5 * (zvar - (xvar + yvar))

            denom = 2 * covar
            num = (yvar - xvar) + np.sqrt((yvar - xvar) * (yvar - xvar) + 4 * (covar * covar))
            a = (num / denom)
            b = (ymean - a * xmean)

            i = 1
            while i > 0.003921568627:
                thr_fi_c = i
                thr_si_c = (a * i) + b
                combt = (fi < thr_fi_c) | (si < thr_si_c)
                costReg = scistat.pearsonr(fi[combt], si[combt])
                if costReg[0] <= 0:
                    break
                i = i - 0.003921568627

            # Costes' thershold for entire image is applied to each object
            fi_above_thr = first_pixels > thr_fi_c
            si_above_thr = second_pixels > thr_si_c
            combined_thresh_c = fi_above_thr & si_above_thr
            fi_thresh_c = first_pixels[combined_thresh_c]
            si_thresh_c = second_pixels[combined_thresh_c]
            if np.any(fi_above_thr):
                tot_fi_thr_c = scind.sum(first_pixels[first_pixels >= thr_fi_c], labels[first_pixels >= thr_fi_c], lrange)
            else:
                tot_fi_thr_c = np.zeros(len(lrange))
            if np.any(si_above_thr):
                tot_si_thr_c = scind.sum(second_pixels[second_pixels >= thr_si_c], labels[second_pixels >= thr_si_c],
                                         lrange)
            else:
                tot_si_thr_c = np.zeros(len(lrange))

            # Manders Coefficient
            M1 = np.zeros(len(lrange))
            M2 = np.zeros(len(lrange))

            if np.any(combined_thresh):
                M1 = np.array(scind.sum(fi_thresh,labels[combined_thresh],lrange)) / np.array(tot_fi_thr)
                M2 = np.array(scind.sum(si_thresh,labels[combined_thresh],lrange)) / np.array(tot_si_thr)
            result += [[first_image_name, second_image_name, object_name,"Mean Manders coeff","%.3f"%np.mean(M1)],
                       [first_image_name, second_image_name, object_name,"Median Manders coeff","%.3f"%np.median(M1)],
                       [first_image_name, second_image_name, object_name,"Min Manders coeff","%.3f"%np.min(M1)],
                       [first_image_name, second_image_name, object_name,"Max Manders coeff","%.3f"%np.max(M1)]]
            result += [[second_image_name, first_image_name, object_name,"Mean Manders coeff","%.3f"%np.mean(M2)],
                       [second_image_name, first_image_name, object_name,"Median Manders coeff","%.3f"%np.median(M2)],
                       [second_image_name, first_image_name, object_name,"Min Manders coeff","%.3f"%np.min(M2)],
                       [second_image_name, first_image_name, object_name,"Max Manders coeff","%.3f"%np.max(M2)]]

            # RWC Coefficient
            RWC1 = np.zeros(len(lrange))
            RWC2 = np.zeros(len(lrange))
            [Rank1] = np.lexsort(([labels], [first_pixels]))
            [Rank2] = np.lexsort(([labels], [second_pixels]))
            Rank1_U = np.hstack([[False], first_pixels[Rank1[:-1]] != first_pixels[Rank1[1:]]])
            Rank2_U = np.hstack([[False], second_pixels[Rank2[:-1]] != second_pixels[Rank2[1:]]])
            Rank1_S = np.cumsum(Rank1_U)
            Rank2_S = np.cumsum(Rank2_U)
            Rank_im1 = np.zeros(first_pixels.shape, dtype=int)
            Rank_im2 = np.zeros(second_pixels.shape, dtype=int)
            Rank_im1[Rank1] = Rank1_S
            Rank_im2[Rank2] = Rank2_S

            R = max(Rank_im1.max(), Rank_im2.max()) + 1
            Di = abs(Rank_im1 - Rank_im2)
            weight = (R - Di) * 1.0 / R
            weight_thresh = weight[combined_thresh]
            if np.any(combined_thresh_c):
                RWC1 = np.array(scind.sum(fi_thresh * weight_thresh, labels[combined_thresh], lrange)) / np.array(
                        tot_fi_thr)
                RWC2 = np.array(scind.sum(si_thresh * weight_thresh, labels[combined_thresh], lrange)) / np.array(
                        tot_si_thr)

            result += [[first_image_name, second_image_name, object_name, "Mean RWC coeff", "%.3f" % np.mean(RWC1)],
                       [first_image_name, second_image_name, object_name, "Median RWC coeff", "%.3f" % np.median(RWC1)],
                       [first_image_name, second_image_name, object_name, "Min RWC coeff", "%.3f" % np.min(RWC1)],
                       [first_image_name, second_image_name, object_name, "Max RWC coeff", "%.3f" % np.max(RWC1)]]
            result += [[second_image_name, first_image_name, object_name, "Mean RWC coeff", "%.3f" % np.mean(RWC2)],
                       [second_image_name, first_image_name, object_name, "Median RWC coeff", "%.3f" % np.median(RWC2)],
                       [second_image_name, first_image_name, object_name, "Min RWC coeff", "%.3f" % np.min(RWC2)],
                       [second_image_name, first_image_name, object_name, "Max RWC coeff", "%.3f" % np.max(RWC2)]]

            # Costes Automated Threshold
            C1 = np.zeros(len(lrange))
            C2 = np.zeros(len(lrange))
            if np.any(combined_thresh_c):
                C1 = np.array(scind.sum(fi_thresh_c,labels[combined_thresh_c],lrange)) / np.array(tot_fi_thr_c)
                C2 = np.array(scind.sum(si_thresh_c,labels[combined_thresh_c],lrange)) / np.array(tot_si_thr_c)
            result += [[first_image_name, second_image_name, object_name,"Mean Manders coeff (Costes)","%.3f"%np.mean(C1)],
                       [first_image_name, second_image_name, object_name,"Median Manders coeff (Costes)","%.3f"%np.median(C1)],
                       [first_image_name, second_image_name, object_name,"Min Manders coeff (Costes)","%.3f"%np.min(C1)],
                       [first_image_name, second_image_name, object_name,"Max Manders coeff (Costes)","%.3f"%np.max(C1)]
                       ]
            result += [[second_image_name, first_image_name, object_name,"Mean Manders coeff (Costes)","%.3f"%np.mean(C2)],
                       [second_image_name, first_image_name, object_name,"Median Manders coeff (Costes)","%.3f"%np.median(C2)],
                       [second_image_name, first_image_name, object_name,"Min Manders coeff (Costes)","%.3f"%np.min(C2)],
                       [second_image_name, first_image_name, object_name,"Max Manders coeff (Costes)","%.3f"%np.max(C2)]
                       ]

            # Overlap Coefficient
            fpsq = scind.sum(first_pixels[combined_thresh] ** 2, labels[combined_thresh], lrange)
            spsq = scind.sum(second_pixels[combined_thresh] ** 2, labels[combined_thresh], lrange)
            pdt = np.sqrt(np.array(fpsq) * np.array(spsq))

            if np.any(combined_thresh):
                overlap = fix(
                        scind.sum(first_pixels[combined_thresh] * second_pixels[combined_thresh],
                                  labels[combined_thresh],
                                  lrange) / pdt)
                K1 = fix((scind.sum(first_pixels[combined_thresh] * second_pixels[combined_thresh],
                                    labels[combined_thresh], lrange)) / (np.array(fpsq)))
                K2 = fix(
                        scind.sum(first_pixels[combined_thresh] * second_pixels[combined_thresh],
                                  labels[combined_thresh],
                                  lrange) / np.array(spsq))
            else:
                overlap = K1 = K2 = np.zeros(len(lrange))
            result += [
                [first_image_name, second_image_name, object_name, "Mean Overlap coeff", "%.3f" % np.mean(overlap)],
                [first_image_name, second_image_name, object_name, "Median Overlap coeff", "%.3f" % np.median(overlap)],
                [first_image_name, second_image_name, object_name, "Min Overlap coeff", "%.3f" % np.min(overlap)],
                [first_image_name, second_image_name, object_name, "Max Overlap coeff", "%.3f" % np.max(overlap)]]

        measurement = ("Correlation_Correlation_%s_%s" %
                       (first_image_name, second_image_name))
        overlap_measurement = (F_OVERLAP_FORMAT % (first_image_name,
                                                   second_image_name))
        k_measurement_1 = (F_K_FORMAT % (first_image_name,
                                         second_image_name))
        k_measurement_2 = (F_K_FORMAT % (second_image_name,
                                         first_image_name))
        manders_measurement_1 = (F_MANDERS_FORMAT % (first_image_name,
                                                     second_image_name))
        manders_measurement_2 = (F_MANDERS_FORMAT % (second_image_name,
                                                     first_image_name))
        rwc_measurement_1 = (F_RWC_FORMAT % (first_image_name,
                                             second_image_name))
        rwc_measurement_2 = (F_RWC_FORMAT % (second_image_name,
                                             first_image_name))
        costes_measurement_1 = (F_COSTES_FORMAT % (first_image_name,
                                                   second_image_name))
        costes_measurement_2 = (F_COSTES_FORMAT % (second_image_name,
                                                   first_image_name))

        workspace.measurements.add_measurement(object_name, measurement, corr)
        workspace.measurements.add_measurement(object_name, overlap_measurement, overlap)
        workspace.measurements.add_measurement(object_name, k_measurement_1, K1)
        workspace.measurements.add_measurement(object_name, k_measurement_2, K2)
        workspace.measurements.add_measurement(object_name, manders_measurement_1, M1)
        workspace.measurements.add_measurement(object_name, manders_measurement_2, M2)
        workspace.measurements.add_measurement(object_name, rwc_measurement_1, RWC1)
        workspace.measurements.add_measurement(object_name, rwc_measurement_2, RWC2)
        workspace.measurements.add_measurement(object_name, costes_measurement_1, C1)
        workspace.measurements.add_measurement(object_name, costes_measurement_2, C2)

        if n_objects == 0:
            return [[first_image_name, second_image_name, object_name,
                     "Mean correlation", "-"],
                    [first_image_name, second_image_name, object_name,
                     "Median correlation", "-"],
                    [first_image_name, second_image_name, object_name,
                     "Min correlation", "-"],
                    [first_image_name, second_image_name, object_name,
                     "Max correlation", "-"]]
        else:
            return result