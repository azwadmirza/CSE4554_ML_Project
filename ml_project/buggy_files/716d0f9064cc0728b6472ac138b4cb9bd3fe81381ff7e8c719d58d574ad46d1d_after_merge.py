    def get_parents_of(self, workspace, parent_name):
        '''Return the parents_of measurment or equivalent

        parent_name - name of parent objects

        Return a vector of parent indexes to the given parent name using
        the Parent measurement. Look for a direct parent / child link first
        and then look for relationships between self.parent_name and the
        named parent.
        '''
        meas = workspace.measurements

        parent_feature = cellprofiler.measurement.FF_PARENT % parent_name

        primary_parent = self.x_name.value

        sub_object_name = self.y_name.value

        primary_parent_feature = cellprofiler.measurement.FF_PARENT % primary_parent

        if parent_feature in meas.get_feature_names(sub_object_name):
            parents_of = meas.get_current_measurement(sub_object_name, parent_feature)
        elif parent_feature in meas.get_feature_names(primary_parent):
            #
            # parent_name is the grandparent of the sub-object via
            # the primary parent.
            #
            primary_parents_of = meas.get_current_measurement(sub_object_name, primary_parent_feature)

            grandparents_of = meas.get_current_measurement(primary_parent, parent_feature)

            mask = primary_parents_of != 0

            parents_of = numpy.zeros(primary_parents_of.shape[0], grandparents_of.dtype)

            if primary_parents_of.shape[0] > 0:
                parents_of[mask] = grandparents_of[primary_parents_of[mask] - 1]
        elif primary_parent_feature in meas.get_feature_names(parent_name):
            primary_parents_of = meas.get_current_measurement(sub_object_name, primary_parent_feature)

            primary_parents_of_parent = meas.get_current_measurement(parent_name, primary_parent_feature)

            if len(primary_parents_of_parent) == 0:
                return primary_parents_of_parent

            #
            # There may not be a 1-1 relationship, but we attempt to
            # construct one
            #
            reverse_lookup_len = max(numpy.max(primary_parents_of) + 1, len(primary_parents_of_parent))

            reverse_lookup = numpy.zeros(reverse_lookup_len, int)

            if primary_parents_of_parent.shape[0] > 0:
                reverse_lookup[primary_parents_of_parent] = numpy.arange(1, len(primary_parents_of_parent) + 1)

            if primary_parents_of.shape[0] > 0:
                parents_of = reverse_lookup[primary_parents_of]
        else:
            raise ValueError("Don't know how to relate {} to {}".format(primary_parent, parent_name))

        return parents_of