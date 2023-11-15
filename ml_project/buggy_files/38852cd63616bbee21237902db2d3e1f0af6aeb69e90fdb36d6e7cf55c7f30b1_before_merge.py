    def calculate_minimum_distances(self, workspace, parent_name):
        '''Calculate the distance from child center to parent perimeter'''
        meas = workspace.measurements

        sub_object_name = self.sub_object_name.value

        parents = workspace.object_set.get_objects(parent_name)

        children = workspace.object_set.get_objects(sub_object_name)

        parents_of = self.get_parents_of(workspace, parent_name)

        if len(parents_of) == 0:
            dist = numpy.zeros((0,))
        elif numpy.all(parents_of == 0):
            dist = numpy.array([numpy.NaN] * len(parents_of))
        else:
            mask = parents_of > 0

            ccenters = centrosome.cpmorphology.centers_of_labels(children.segmented).transpose()

            ccenters = ccenters[mask, :]

            parents_of_masked = parents_of[mask] - 1

            pperim = centrosome.outline.outline(parents.segmented)

            # Get a list of all points on the perimeter
            perim_loc = numpy.argwhere(pperim != 0)

            # Get the label # for each point
            perim_idx = pperim[perim_loc[:, 0], perim_loc[:, 1]]

            # Sort the points by label #
            idx = numpy.lexsort((perim_loc[:, 1], perim_loc[:, 0], perim_idx))

            perim_loc = perim_loc[idx, :]

            perim_idx = perim_idx[idx]

            # Get counts and indexes to each run of perimeter points
            counts = centrosome.cpmorphology.fixup_scipy_ndimage_result(
                scipy.ndimage.sum(
                    numpy.ones(len(perim_idx)),
                    perim_idx,
                    numpy.arange(1, perim_idx[-1] + 1))
            ).astype(numpy.int32)

            indexes = numpy.cumsum(counts) - counts

            # For the children, get the index and count of the parent
            ccounts = counts[parents_of_masked]

            cindexes = indexes[parents_of_masked]

            # Now make an array that has an element for each of that child's perimeter points
            clabel = numpy.zeros(numpy.sum(ccounts), int)

            # cfirst is the eventual first index of each child in the clabel array
            cfirst = numpy.cumsum(ccounts) - ccounts

            clabel[cfirst[1:]] += 1

            clabel = numpy.cumsum(clabel)

            # Make an index that runs from 0 to ccounts for each child label.
            cp_index = numpy.arange(len(clabel)) - cfirst[clabel]

            # then add cindexes to get an index to the perimeter point
            cp_index += cindexes[clabel]

            # Now, calculate the distance from the centroid of each label to each perimeter point in the parent.
            dist = numpy.sqrt(numpy.sum((perim_loc[cp_index, :] - ccenters[clabel, :]) ** 2, 1))

            # Finally, find the minimum distance per child
            min_dist = centrosome.cpmorphology.fixup_scipy_ndimage_result(
                scipy.ndimage.minimum(dist, clabel, numpy.arange(len(ccounts)))
            )

            # Account for unparented children
            dist = numpy.array([numpy.NaN] * len(mask))

            dist[mask] = min_dist

        meas.add_measurement(sub_object_name, FF_MINIMUM % parent_name, dist)