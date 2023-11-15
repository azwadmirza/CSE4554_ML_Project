    def run(self, workspace):
        objects = workspace.object_set.get_objects(self.object_name.value)
        assert isinstance(objects, cpo.Objects)
        has_pixels = objects.areas > 0
        labels = objects.small_removed_segmented
        kept_labels = objects.segmented
        neighbor_objects = workspace.object_set.get_objects(self.neighbors_name.value)
        assert isinstance(neighbor_objects, cpo.Objects)
        neighbor_labels = neighbor_objects.small_removed_segmented
        #
        # Need to add in labels touching border.
        #
        unedited_segmented = neighbor_objects.unedited_segmented
        touching_border = np.zeros(np.max(unedited_segmented) + 1, bool)
        touching_border[unedited_segmented[0, :]] = True
        touching_border[unedited_segmented[-1, :]] = True
        touching_border[unedited_segmented[:, 0]] = True
        touching_border[unedited_segmented[:, -1]] = True
        touching_border[0] = False
        touching_border_mask = touching_border[unedited_segmented]
        nobjects = np.max(labels)
        nneighbors = np.max(neighbor_labels)
        nkept_objects = objects.count
        if np.any(touching_border) and \
           np.all(~ touching_border_mask[neighbor_labels!=0]):
            # Add the border labels if any were excluded
            touching_border_object_number = np.cumsum(touching_border) + \
                np.max(neighbor_labels)
            touching_border_mask = touching_border_mask & neighbor_labels == 0
            neighbor_labels = neighbor_labels.copy().astype(np.int32)
            neighbor_labels[touching_border_mask] = touching_border_object_number[
                unedited_segmented[touching_border_mask]]
        
        _, object_numbers = objects.relate_labels(labels, kept_labels)
        if self.neighbors_are_objects:
            neighbor_numbers = object_numbers
        else:
            _, neighbor_numbers = neighbor_objects.relate_labels(
                neighbor_labels, neighbor_objects.segmented)
        neighbor_count = np.zeros((nobjects,))
        pixel_count = np.zeros((nobjects,))
        first_object_number = np.zeros((nobjects,),int)
        second_object_number = np.zeros((nobjects,),int)
        first_x_vector = np.zeros((nobjects,))
        second_x_vector = np.zeros((nobjects,))
        first_y_vector = np.zeros((nobjects,))
        second_y_vector = np.zeros((nobjects,))
        angle = np.zeros((nobjects,))
        percent_touching = np.zeros((nobjects,))
        expanded_labels = None
        if self.distance_method == D_EXPAND:
            # Find the i,j coordinates of the nearest foreground point
            # to every background point
            i,j = scind.distance_transform_edt(labels==0,
                                               return_distances=False,
                                               return_indices=True)
            # Assign each background pixel to the label of its nearest
            # foreground pixel. Assign label to label for foreground.
            labels = labels[i,j]
            expanded_labels = labels  # for display
            distance = 1 # dilate once to make touching edges overlap
            scale = S_EXPANDED
            if self.neighbors_are_objects:
                neighbor_labels = labels.copy()
        elif self.distance_method == D_WITHIN:
            distance = self.distance.value
            scale = str(distance)
        elif self.distance_method == D_ADJACENT:
            distance = 1
            scale = S_ADJACENT
        else:
            raise ValueError("Unknown distance method: %s" %
                             self.distance_method.value)
        if nneighbors > (1 if self.neighbors_are_objects else 0):
            first_objects = []
            second_objects = []
            object_indexes = np.arange(nobjects, dtype=np.int32)+1
            #
            # First, compute the first and second nearest neighbors,
            # and the angles between self and the first and second
            # nearest neighbors
            #
            ocenters = centers_of_labels(
                objects.small_removed_segmented).transpose()
            ncenters = centers_of_labels(
                neighbor_objects.small_removed_segmented).transpose()
            areas = fix(scind.sum(np.ones(labels.shape),labels, object_indexes))
            perimeter_outlines = outline(labels)
            perimeters = fix(scind.sum(
                np.ones(labels.shape), perimeter_outlines, object_indexes))
                                       
            i,j = np.mgrid[0:nobjects,0:nneighbors]
            distance_matrix = np.sqrt((ocenters[i,0] - ncenters[j,0])**2 +
                                      (ocenters[i,1] - ncenters[j,1])**2)
            #
            # order[:,0] should be arange(nobjects)
            # order[:,1] should be the nearest neighbor
            # order[:,2] should be the next nearest neighbor
            #
            if distance_matrix.shape[1] == 1:
                # a little buggy, lexsort assumes that a 2-d array of
                # second dimension = 1 is a 1-d array
                order = np.zeros(distance_matrix.shape, int)
            else:
                order = np.lexsort([distance_matrix])
            first_neighbor = 1 if self.neighbors_are_objects else 0
            first_object_index = order[:, first_neighbor]
            first_x_vector = ncenters[first_object_index,1] - ocenters[:,1]
            first_y_vector = ncenters[first_object_index,0] - ocenters[:,0]
            if nneighbors > first_neighbor+1:
                second_object_index = order[:, first_neighbor + 1]
                second_x_vector = ncenters[second_object_index,1] - ocenters[:,1]
                second_y_vector = ncenters[second_object_index,0] - ocenters[:,0]
                v1 = np.array((first_x_vector,first_y_vector))
                v2 = np.array((second_x_vector,second_y_vector))
                #
                # Project the unit vector v1 against the unit vector v2
                #
                dot = (np.sum(v1*v2,0) / 
                       np.sqrt(np.sum(v1**2,0)*np.sum(v2**2,0)))
                angle = np.arccos(dot) * 180. / np.pi
            
            # Make the structuring element for dilation
            strel = strel_disk(distance)
            #
            # A little bigger one to enter into the border with a structure
            # that mimics the one used to create the outline
            #
            strel_touching = strel_disk(distance + .5)
            #
            # Get the extents for each object and calculate the patch
            # that excises the part of the image that is "distance"
            # away
            i,j = np.mgrid[0:labels.shape[0],0:labels.shape[1]]
            min_i, max_i, min_i_pos, max_i_pos =\
                scind.extrema(i,labels,object_indexes)
            min_j, max_j, min_j_pos, max_j_pos =\
                scind.extrema(j,labels,object_indexes)
            min_i = np.maximum(fix(min_i)-distance,0).astype(int)
            max_i = np.minimum(fix(max_i)+distance+1,labels.shape[0]).astype(int)
            min_j = np.maximum(fix(min_j)-distance,0).astype(int)
            max_j = np.minimum(fix(max_j)+distance+1,labels.shape[1]).astype(int)
            #
            # Loop over all objects
            # Calculate which ones overlap "index"
            # Calculate how much overlap there is of others to "index"
            #
            for object_number in object_numbers:
                if object_number == 0:
                    #
                    # No corresponding object in small-removed. This means
                    # that the object has no pixels, e.g. not renumbered.
                    #
                    continue
                index = object_number - 1
                patch = labels[min_i[index]:max_i[index],
                               min_j[index]:max_j[index]]
                npatch = neighbor_labels[min_i[index]:max_i[index],
                                         min_j[index]:max_j[index]]
                #
                # Find the neighbors
                #
                patch_mask = patch==(index+1)
                extended = scind.binary_dilation(patch_mask,strel)
                neighbors = np.unique(npatch[extended])
                neighbors = neighbors[neighbors != 0]
                if self.neighbors_are_objects:
                    neighbors = neighbors[neighbors != object_number]
                nc = len(neighbors)
                neighbor_count[index] = nc
                if nc > 0:
                    first_objects.append(np.ones(nc,int) * object_number)
                    second_objects.append(neighbors)
                if self.neighbors_are_objects:
                    #
                    # Find the # of overlapping pixels. Dilate the neighbors
                    # and see how many pixels overlap our image. Use a 3x3
                    # structuring element to expand the overlapping edge
                    # into the perimeter.
                    #
                    outline_patch = perimeter_outlines[
                        min_i[index]:max_i[index],
                        min_j[index]:max_j[index]] == object_number
                    extended = scind.binary_dilation(
                        (patch != 0) & (patch != object_number), strel_touching)
                    overlap = np.sum(outline_patch & extended)
                    pixel_count[index] = overlap
            if sum([len(x) for x in first_objects]) > 0:
                first_objects = np.hstack(first_objects)
                reverse_object_numbers = np.zeros(
                    max(np.max(object_numbers), np.max(first_objects)) + 1, int)
                reverse_object_numbers[object_numbers] = np.arange(len(object_numbers)) + 1
                first_objects = reverse_object_numbers[first_objects]
    
                second_objects = np.hstack(second_objects)
                reverse_neighbor_numbers = np.zeros(
                    max(np.max(neighbor_numbers), np.max(second_objects)) + 1, int)
                reverse_neighbor_numbers[neighbor_numbers] = np.arange(len(neighbor_numbers)) + 1
                second_objects= reverse_neighbor_numbers[second_objects]
                to_keep = (first_objects > 0) & (second_objects > 0)
                first_objects = first_objects[to_keep]
                second_objects  = second_objects[to_keep]
            else:
                first_objects = np.zeros(0, int)
                second_objects = np.zeros(0, int)
            if self.neighbors_are_objects:
                percent_touching = pixel_count * 100 / perimeters
            else:
                percent_touching = pixel_count * 100.0 / areas
            object_indexes = object_numbers - 1
            neighbor_indexes = neighbor_numbers - 1
            #
            # Have to recompute nearest
            #
            first_object_number = np.zeros(nkept_objects, int)
            second_object_number = np.zeros(nkept_objects, int)
            if nkept_objects > (1 if self.neighbors_are_objects else 0):
                di = (ocenters[object_indexes[:, np.newaxis], 0] - 
                      ncenters[neighbor_indexes[np.newaxis, :], 0])
                dj = (ocenters[object_indexes[:, np.newaxis], 1] - 
                      ncenters[neighbor_indexes[np.newaxis, :], 1])
                distance_matrix = np.sqrt(di*di + dj*dj)
                distance_matrix[~ has_pixels, :] = np.inf
                distance_matrix[:, ~has_pixels] = np.inf
                #
                # order[:,0] should be arange(nobjects)
                # order[:,1] should be the nearest neighbor
                # order[:,2] should be the next nearest neighbor
                #
                order = np.lexsort([distance_matrix]).astype(
                    first_object_number.dtype)
                if self.neighbors_are_objects:
                    first_object_number[has_pixels] = order[has_pixels,1] + 1
                    if nkept_objects > 2:
                        second_object_number[has_pixels] = order[has_pixels,2] + 1
                else:
                    first_object_number[has_pixels] = order[has_pixels,0] + 1
                    if nneighbors > 1:
                        second_object_number[has_pixels] = order[has_pixels,1] + 1
        else:
            object_indexes = object_numbers - 1
            neighbor_indexes = neighbor_numbers - 1
            first_objects = np.zeros(0, int)
            second_objects = np.zeros(0, int)
        #
        # Now convert all measurements from the small-removed to
        # the final number set.
        #
        neighbor_count = neighbor_count[object_indexes]
        neighbor_count[~ has_pixels] = 0
        percent_touching = percent_touching[object_indexes]
        percent_touching[~ has_pixels] = 0
        first_x_vector = first_x_vector[object_indexes]
        second_x_vector = second_x_vector[object_indexes]
        first_y_vector = first_y_vector[object_indexes]
        second_y_vector = second_y_vector[object_indexes]
        angle = angle[object_indexes]
        #
        # Record the measurements
        #
        assert(isinstance(workspace, cpw.Workspace))
        m = workspace.measurements
        assert(isinstance(m, cpmeas.Measurements))
        image_set = workspace.image_set
        features_and_data = [
            (M_NUMBER_OF_NEIGHBORS, neighbor_count),
            (M_FIRST_CLOSEST_OBJECT_NUMBER, first_object_number),
            (M_FIRST_CLOSEST_DISTANCE, np.sqrt(first_x_vector**2+first_y_vector**2)),
            (M_SECOND_CLOSEST_OBJECT_NUMBER, second_object_number),
            (M_SECOND_CLOSEST_DISTANCE, np.sqrt(second_x_vector**2+second_y_vector**2)),
            (M_ANGLE_BETWEEN_NEIGHBORS, angle)]
        if self.neighbors_are_objects:
            features_and_data.append((M_PERCENT_TOUCHING, percent_touching))
        for feature_name, data in features_and_data:
            m.add_measurement(self.object_name.value,
                              self.get_measurement_name(feature_name),
                              data)
        if len(first_objects) > 0:
            m.add_relate_measurement(
                self.module_num, 
                cpmeas.NEIGHBORS,
                self.object_name.value,
                self.object_name.value if self.neighbors_are_objects 
                else self.neighbors_name.value,
                m.image_set_number * np.ones(first_objects.shape, int),
                first_objects,
                m.image_set_number * np.ones(second_objects.shape, int),
                second_objects)
                                 
        labels = kept_labels
        
        neighbor_count_image = np.zeros(labels.shape,int)
        object_mask = objects.segmented != 0
        object_indexes = objects.segmented[object_mask]-1
        neighbor_count_image[object_mask] = neighbor_count[object_indexes]
        workspace.display_data.neighbor_count_image = neighbor_count_image
        
        if self.neighbors_are_objects:
            percent_touching_image = np.zeros(labels.shape)
            percent_touching_image[object_mask] = percent_touching[object_indexes]
            workspace.display_data.percent_touching_image = percent_touching_image
        
        image_set = workspace.image_set
        if self.wants_count_image.value:
            neighbor_cm_name = self.count_colormap.value
            neighbor_cm = get_colormap(neighbor_cm_name)
            sm = matplotlib.cm.ScalarMappable(cmap = neighbor_cm)
            img = sm.to_rgba(neighbor_count_image)[:,:,:3]
            img[:,:,0][~ object_mask] = 0
            img[:,:,1][~ object_mask] = 0
            img[:,:,2][~ object_mask] = 0
            count_image = cpi.Image(img, masking_objects = objects)
            image_set.add(self.count_image_name.value, count_image)
        else:
            neighbor_cm_name = cpprefs.get_default_colormap()
            neighbor_cm = matplotlib.cm.get_cmap(neighbor_cm_name)
        if self.neighbors_are_objects and self.wants_percent_touching_image:
            percent_touching_cm_name = self.touching_colormap.value
            percent_touching_cm = get_colormap(percent_touching_cm_name)
            sm = matplotlib.cm.ScalarMappable(cmap = percent_touching_cm)
            img = sm.to_rgba(percent_touching_image)[:,:,:3]
            img[:,:,0][~ object_mask] = 0
            img[:,:,1][~ object_mask] = 0
            img[:,:,2][~ object_mask] = 0
            touching_image = cpi.Image(img, masking_objects = objects)
            image_set.add(self.touching_image_name.value,
                          touching_image)
        else:
            percent_touching_cm_name = cpprefs.get_default_colormap()
            percent_touching_cm = matplotlib.cm.get_cmap(percent_touching_cm_name)

        if self.show_window:
            workspace.display_data.neighbor_cm_name = neighbor_cm_name
            workspace.display_data.percent_touching_cm_name = percent_touching_cm_name
            workspace.display_data.orig_labels = objects.segmented
            workspace.display_data.expanded_labels = expanded_labels
            workspace.display_data.object_mask = object_mask