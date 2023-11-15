    def run_on_objects(self, object_name, workspace):
        """Run, computing the area measurements for a single map of objects"""
        objects = workspace.get_objects(object_name)

        if len(objects.shape) == 2:
            #
            # Do the ellipse-related measurements
            #
            i, j, l = objects.ijv.transpose()
            centers, eccentricity, major_axis_length, minor_axis_length, \
            theta, compactness = \
                ellipse_from_second_moments_ijv(i, j, 1, l, objects.indices, True)
            del i
            del j
            del l
            self.record_measurement(workspace, object_name,
                                    F_ECCENTRICITY, eccentricity)
            self.record_measurement(workspace, object_name,
                                    F_MAJOR_AXIS_LENGTH, major_axis_length)
            self.record_measurement(workspace, object_name,
                                    F_MINOR_AXIS_LENGTH, minor_axis_length)
            self.record_measurement(workspace, object_name, F_ORIENTATION,
                                    theta * 180 / np.pi)
            self.record_measurement(workspace, object_name, F_COMPACTNESS,
                                    compactness)
            is_first = False
            if len(objects.indices) == 0:
                nobjects = 0
            else:
                nobjects = np.max(objects.indices)
            mcenter_x = np.zeros(nobjects)
            mcenter_y = np.zeros(nobjects)
            mextent = np.zeros(nobjects)
            mperimeters = np.zeros(nobjects)
            msolidity = np.zeros(nobjects)
            euler = np.zeros(nobjects)
            max_radius = np.zeros(nobjects)
            median_radius = np.zeros(nobjects)
            mean_radius = np.zeros(nobjects)
            min_feret_diameter = np.zeros(nobjects)
            max_feret_diameter = np.zeros(nobjects)
            zernike_numbers = self.get_zernike_numbers()
            zf = {}
            for n, m in zernike_numbers:
                zf[(n, m)] = np.zeros(nobjects)
            if nobjects > 0:
                chulls, chull_counts = convex_hull_ijv(objects.ijv, objects.indices)
                for labels, indices in objects.get_labels():
                    to_indices = indices - 1
                    distances = distance_to_edge(labels)
                    mcenter_y[to_indices], mcenter_x[to_indices] = \
                        maximum_position_of_labels(distances, labels, indices)
                    max_radius[to_indices] = fix(scind.maximum(
                            distances, labels, indices))
                    mean_radius[to_indices] = fix(scind.mean(
                            distances, labels, indices))
                    median_radius[to_indices] = median_of_labels(
                            distances, labels, indices)
                    #
                    # The extent (area / bounding box area)
                    #
                    mextent[to_indices] = calculate_extents(labels, indices)
                    #
                    # The perimeter distance
                    #
                    mperimeters[to_indices] = calculate_perimeters(labels, indices)
                    #
                    # Solidity
                    #
                    msolidity[to_indices] = calculate_solidity(labels, indices)
                    #
                    # Euler number
                    #
                    euler[to_indices] = euler_number(labels, indices)
                    #
                    # Zernike features
                    #
                    zf_l = cpmz.zernike(zernike_numbers, labels, indices)
                    for (n, m), z in zip(zernike_numbers, zf_l.transpose()):
                        zf[(n, m)][to_indices] = z
                #
                # Form factor
                #
                ff = 4.0 * np.pi * objects.areas / mperimeters ** 2
                #
                # Feret diameter
                #
                min_feret_diameter, max_feret_diameter = \
                    feret_diameter(chulls, chull_counts, objects.indices)

            else:
                ff = np.zeros(0)

            for f, m in ([(F_AREA, objects.areas),
                          (F_CENTER_X, mcenter_x),
                          (F_CENTER_Y, mcenter_y),
                          (F_CENTER_Z, np.ones_like(mcenter_x)),
                          (F_EXTENT, mextent),
                          (F_PERIMETER, mperimeters),
                          (F_SOLIDITY, msolidity),
                          (F_FORM_FACTOR, ff),
                          (F_EULER_NUMBER, euler),
                          (F_MAXIMUM_RADIUS, max_radius),
                          (F_MEAN_RADIUS, mean_radius),
                          (F_MEDIAN_RADIUS, median_radius),
                          (F_MIN_FERET_DIAMETER, min_feret_diameter),
                          (F_MAX_FERET_DIAMETER, max_feret_diameter)] +
                             [(self.get_zernike_name((n, m)), zf[(n, m)])
                              for n, m in zernike_numbers]):
                self.record_measurement(workspace, object_name, f, m)
        else:
            labels = objects.segmented

            props = skimage.measure.regionprops(labels)

            # Area
            areas = [prop.area for prop in props]

            self.record_measurement(workspace, object_name, F_AREA, areas)

            # Extent
            extents = [prop.extent for prop in props]

            self.record_measurement(workspace, object_name, F_EXTENT, extents)

            # Centers of mass
            import mahotas

            if objects.has_parent_image:
                image = objects.parent_image

                data = image.pixel_data

                spacing = image.spacing
            else:
                data = np.ones_like(labels)

                spacing = (1.0, 1.0, 1.0)

            centers = mahotas.center_of_mass(data, labels=labels)

            if np.any(labels == 0):
                # Remove the 0-label center of mass
                centers = centers[1:]

            center_z, center_x, center_y = centers.transpose()

            self.record_measurement(workspace, object_name, F_CENTER_X, center_x)

            self.record_measurement(workspace, object_name, F_CENTER_Y, center_y)

            self.record_measurement(workspace, object_name, F_CENTER_Z, center_z)

            # Perimeters
            perimeters = []

            for label in np.unique(labels):
                if label == 0:
                    continue

                volume = np.zeros_like(labels, dtype='bool')

                volume[labels == label] = True

                verts, faces, _, _ = skimage.measure.marching_cubes(
                    volume,
                    spacing=spacing,
                    level=0
                )

                perimeters += [skimage.measure.mesh_surface_area(verts, faces)]

            if len(perimeters) == 0:
                self.record_measurement(workspace, object_name, F_PERIMETER, [0])
            else:
                self.record_measurement(workspace, object_name, F_PERIMETER, perimeters)

            for feature in self.get_feature_names():
                if feature in [F_AREA, F_EXTENT, F_CENTER_X, F_CENTER_Y, F_CENTER_Z, F_PERIMETER]:
                    continue

                self.record_measurement(workspace, object_name, feature, [np.nan])