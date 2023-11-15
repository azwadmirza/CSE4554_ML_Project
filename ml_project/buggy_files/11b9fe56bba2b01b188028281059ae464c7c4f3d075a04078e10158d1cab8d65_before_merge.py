    def do_measurements(self, workspace, image_name, object_name, 
                        center_object_name, center_choice,
                        bin_count_settings, dd):
        '''Perform the radial measurements on the image set
        
        workspace - workspace that holds images / objects
        image_name - make measurements on this image
        object_name - make measurements on these objects
        center_object_name - use the centers of these related objects as
                      the centers for radial measurements. None to use the
                      objects themselves.
        center_choice - the user's center choice for this object:
                      C_SELF, C_CENTERS_OF_OBJECTS or C_EDGES_OF_OBJECTS.
        bin_count_settings - the bin count settings group
        d - a dictionary for saving reusable partial results
        
        returns one statistics tuple per ring.
        '''
        assert isinstance(workspace, cpw.Workspace)
        assert isinstance(workspace.object_set, cpo.ObjectSet)
        bin_count = bin_count_settings.bin_count.value
        wants_scaled = bin_count_settings.wants_scaled.value
        maximum_radius = bin_count_settings.maximum_radius.value
        
        image = workspace.image_set.get_image(image_name,
                                              must_be_grayscale=True)
        objects = workspace.object_set.get_objects(object_name)
        labels, pixel_data = cpo.crop_labels_and_image(objects.segmented,
                                                       image.pixel_data)
        nobjects = np.max(objects.segmented)
        measurements = workspace.measurements
        assert isinstance(measurements, cpmeas.Measurements)
        if nobjects == 0:
            for bin in range(1, bin_count+1):
                for feature in (F_FRAC_AT_D, F_MEAN_FRAC, F_RADIAL_CV):
                    feature_name = (
                        (feature + FF_GENERIC) % (image_name, bin, bin_count))
                    measurements.add_measurement(
                        object_name, "_".join([M_CATEGORY, feature_name]),
                        np.zeros(0))
                    if not wants_scaled:
                        measurement_name = "_".join([M_CATEGORY, feature,
                                                     image_name, FF_OVERFLOW])
                        measurements.add_measurement(
                            object_name, measurement_name, np.zeros(0))
            return [(image_name, object_name, "no objects","-","-","-","-")]
        name = (object_name if center_object_name is None 
                else "%s_%s"%(object_name, center_object_name))
        if dd.has_key(name):
            normalized_distance, i_center, j_center, good_mask = dd[name]
        else:
            d_to_edge = distance_to_edge(labels)
            if center_object_name is not None:
                #
                # Use the center of the centering objects to assign a center
                # to each labeled pixel using propagation
                #
                center_objects=workspace.object_set.get_objects(center_object_name)
                center_labels, cmask = cpo.size_similarly(
                    labels, center_objects.segmented)
                pixel_counts = fix(scind.sum(
                    np.ones(center_labels.shape),
                    center_labels,
                    np.arange(1, np.max(center_labels)+1,dtype=np.int32)))
                good = pixel_counts > 0
                i,j = (centers_of_labels(center_labels) + .5).astype(int)
                if center_choice == C_CENTERS_OF_OTHER:
                    #
                    # Reduce the propagation labels to the centers of
                    # the centering objects
                    #
                    ig = i[good]
                    jg = j[good]
                    lg = np.arange(1, len(i)+1)[good]
                    center_labels = np.zeros(center_labels.shape, int)
                    center_labels[ig,jg] = lg
                cl,d_from_center = propagate(np.zeros(center_labels.shape),
                                             center_labels,
                                             labels != 0, 1)
                #
                # Erase the centers that fall outside of labels
                #
                cl[labels == 0] = 0
                #
                # If objects are hollow or crescent-shaped, there may be
                # objects without center labels. As a backup, find the
                # center that is the closest to the center of mass.
                #
                missing_mask = (labels != 0) & (cl == 0)
                missing_labels = np.unique(labels[missing_mask])
                if len(missing_labels):
                    all_centers = centers_of_labels(labels)
                    missing_i_centers, missing_j_centers = \
                                     all_centers[:, missing_labels-1]
                    di = missing_i_centers[:, np.newaxis] - ig[np.newaxis, :]
                    dj = missing_j_centers[:, np.newaxis] - jg[np.newaxis, :]
                    missing_best = lg[np.lexsort((di*di + dj*dj, ))[:, 0]]
                    best = np.zeros(np.max(labels) + 1, int)
                    best[missing_labels] = missing_best
                    cl[missing_mask] = best[labels[missing_mask]]
                    #
                    # Now compute the crow-flies distance to the centers
                    # of these pixels from whatever center was assigned to
                    # the object.
                    #
                    iii, jjj = np.mgrid[0:labels.shape[0], 0:labels.shape[1]]
                    di = iii[missing_mask] - i[cl[missing_mask] - 1]
                    dj = jjj[missing_mask] - j[cl[missing_mask] - 1]
                    d_from_center[missing_mask] = np.sqrt(di*di + dj*dj)
            else:
                # Find the point in each object farthest away from the edge.
                # This does better than the centroid:
                # * The center is within the object
                # * The center tends to be an interesting point, like the
                #   center of the nucleus or the center of one or the other
                #   of two touching cells.
                #
                i,j = maximum_position_of_labels(d_to_edge, labels, objects.indices)
                center_labels = np.zeros(labels.shape, int)
                center_labels[i,j] = labels[i,j]
                #
                # Use the coloring trick here to process touching objects
                # in separate operations
                #
                colors = color_labels(labels)
                ncolors = np.max(colors)
                d_from_center = np.zeros(labels.shape)
                cl = np.zeros(labels.shape, int)
                for color in range(1,ncolors+1):
                    mask = colors == color
                    l,d = propagate(np.zeros(center_labels.shape),
                                    center_labels,
                                    mask, 1)
                    d_from_center[mask] = d[mask]
                    cl[mask] = l[mask]
            good_mask = cl > 0
            if center_choice == C_EDGES_OF_OTHER:
                # Exclude pixels within the centering objects
                # when performing calculations from the centers
                good_mask = good_mask & (center_labels == 0)
            i_center = np.zeros(cl.shape)
            i_center[good_mask] = i[cl[good_mask]-1]
            j_center = np.zeros(cl.shape)
            j_center[good_mask] = j[cl[good_mask]-1]
            
            normalized_distance = np.zeros(labels.shape)
            if wants_scaled:
                total_distance = d_from_center + d_to_edge
                normalized_distance[good_mask] = (d_from_center[good_mask] /
                                                  (total_distance[good_mask] + .001))
            else:
                normalized_distance[good_mask] = \
                    d_from_center[good_mask] / maximum_radius
            dd[name] = [normalized_distance, i_center, j_center, good_mask]
        ngood_pixels = np.sum(good_mask)
        good_labels = labels[good_mask]
        bin_indexes = (normalized_distance * bin_count).astype(int)
        bin_indexes[bin_indexes > bin_count] = bin_count
        labels_and_bins = (good_labels-1,bin_indexes[good_mask])
        histogram = coo_matrix((pixel_data[good_mask], labels_and_bins),
                               (nobjects, bin_count+1)).toarray()
        sum_by_object = np.sum(histogram, 1)
        sum_by_object_per_bin = np.dstack([sum_by_object]*(bin_count + 1))[0]
        fraction_at_distance = histogram / sum_by_object_per_bin
        number_at_distance = coo_matrix((np.ones(ngood_pixels),labels_and_bins),
                                        (nobjects, bin_count+1)).toarray()
        object_mask = number_at_distance > 0
        sum_by_object = np.sum(number_at_distance, 1)
        sum_by_object_per_bin = np.dstack([sum_by_object]*(bin_count+1))[0]
        fraction_at_bin = number_at_distance / sum_by_object_per_bin
        mean_pixel_fraction = fraction_at_distance / (fraction_at_bin +
                                                      np.finfo(float).eps)
        masked_fraction_at_distance = masked_array(fraction_at_distance,
                                                   ~object_mask)
        masked_mean_pixel_fraction = masked_array(mean_pixel_fraction,
                                                  ~object_mask)
        # Anisotropy calculation.  Split each cell into eight wedges, then
        # compute coefficient of variation of the wedges' mean intensities
        # in each ring.
        #
        # Compute each pixel's delta from the center object's centroid
        i,j = np.mgrid[0:labels.shape[0], 0:labels.shape[1]]
        imask = i[good_mask] > i_center[good_mask]
        jmask = j[good_mask] > j_center[good_mask]
        absmask = (abs(i[good_mask] - i_center[good_mask]) > 
                   abs(j[good_mask] - j_center[good_mask]))
        radial_index = (imask.astype(int) + jmask.astype(int)*2 + 
                        absmask.astype(int)*4)
        statistics = []
        for bin in range(bin_count + (0 if wants_scaled else 1)):
            bin_mask = (good_mask & (bin_indexes == bin))
            bin_pixels = np.sum(bin_mask)
            bin_labels = labels[bin_mask]
            bin_radial_index = radial_index[bin_indexes[good_mask] == bin]
            labels_and_radii = (bin_labels-1, bin_radial_index)
            radial_values = coo_matrix((pixel_data[bin_mask],
                                        labels_and_radii),
                                       (nobjects, 8)).toarray()
            pixel_count = coo_matrix((np.ones(bin_pixels), labels_and_radii),
                                     (nobjects, 8)).toarray()
            mask = pixel_count==0
            radial_means = masked_array(radial_values / pixel_count, mask)
            radial_cv = np.std(radial_means,1) / np.mean(radial_means, 1)
            radial_cv[np.sum(~mask,1)==0] = 0
            for measurement, feature, overflow_feature in (
                (fraction_at_distance[:,bin], MF_FRAC_AT_D, OF_FRAC_AT_D),
                (mean_pixel_fraction[:,bin], MF_MEAN_FRAC, OF_MEAN_FRAC),
                (np.array(radial_cv), MF_RADIAL_CV, OF_RADIAL_CV)):
                
                if bin == bin_count:
                    measurement_name = overflow_feature % image_name
                else:
                    measurement_name = feature % (image_name, bin+1, bin_count)
                measurements.add_measurement(object_name,
                                             measurement_name,
                                             measurement)
            radial_cv.mask = np.sum(~mask,1)==0
            bin_name = str(bin+1) if bin < bin_count else "Overflow"
            statistics += [(image_name, object_name, bin_name, str(bin_count),
                            round(np.mean(masked_fraction_at_distance[:,bin]),4),
                            round(np.mean(masked_mean_pixel_fraction[:, bin]),4),
                            round(np.mean(radial_cv),4))]
        return statistics