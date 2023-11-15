    def calculate_centroid_distances(self, workspace, parent_name):
        '''Calculate the centroid-centroid distance between parent & child'''
        meas = workspace.measurements

        sub_object_name = self.y_name.value

        parents = workspace.object_set.get_objects(parent_name)

        children = workspace.object_set.get_objects(sub_object_name)

        parents_of = self.get_parents_of(workspace, parent_name)

        pcenters = parents.center_of_mass()

        ccenters = children.center_of_mass()

        if pcenters.shape[0] == 0 or ccenters.shape[0] == 0:
            dist = numpy.array([numpy.NaN] * len(parents_of))
        else:
            #
            # Make indexing of parents_of be same as pcenters
            #
            parents_of = parents_of - 1

            mask = (parents_of != -1) | (parents_of > pcenters.shape[0])

            dist = numpy.array([numpy.NaN] * ccenters.shape[0])

            dist[mask] = numpy.sqrt(numpy.sum((ccenters[mask, :] - pcenters[parents_of[mask], :]) ** 2, 1))

        meas.add_measurement(sub_object_name, FF_CENTROID % parent_name, dist)