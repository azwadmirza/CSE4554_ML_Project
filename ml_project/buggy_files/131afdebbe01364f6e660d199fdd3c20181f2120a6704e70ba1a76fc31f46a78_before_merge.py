    def run(self, workspace):
        parents = workspace.object_set.get_objects(self.parent_name.value)

        children = workspace.object_set.get_objects(self.sub_object_name.value)

        child_count, parents_of = parents.relate_children(children)

        m = workspace.measurements

        m.add_measurement(
            self.sub_object_name.value,
            cellprofiler.measurement.FF_PARENT % self.parent_name.value,
            parents_of
        )

        m.add_measurement(
            self.parent_name.value,
            cellprofiler.measurement.FF_CHILDREN_COUNT % self.sub_object_name.value,
            child_count
        )

        good_parents = parents_of[parents_of != 0]

        image_numbers = numpy.ones(len(good_parents), int) * m.image_set_number

        good_children = numpy.argwhere(parents_of != 0).flatten() + 1

        if numpy.any(good_parents):
            m.add_relate_measurement(
                self.module_num,
                cellprofiler.measurement.R_PARENT,
                self.parent_name.value,
                self.sub_object_name.value,
                image_numbers,
                good_parents,
                image_numbers,
                good_children
            )

            m.add_relate_measurement(
                self.module_num,
                cellprofiler.measurement.R_CHILD,
                self.sub_object_name.value,
                self.parent_name.value,
                image_numbers,
                good_children,
                image_numbers,
                good_parents
            )

        parent_names = self.get_parent_names()

        for parent_name in parent_names:
            if self.find_parent_child_distances in (D_BOTH, D_CENTROID):
                self.calculate_centroid_distances(workspace, parent_name)

            if self.find_parent_child_distances in (D_BOTH, D_MINIMUM):
                self.calculate_minimum_distances(workspace, parent_name)

        if self.wants_per_parent_means.value:
            parent_indexes = numpy.arange(numpy.max(parents.segmented)) + 1

            for feature_name in m.get_feature_names(self.sub_object_name.value):
                if not self.should_aggregate_feature(feature_name):
                    continue

                data = m.get_current_measurement(self.sub_object_name.value, feature_name)

                if data is not None and len(data) > 0:
                    if len(parents_of) > 0:
                        means = centrosome.cpmorphology.fixup_scipy_ndimage_result(
                            scipy.ndimage.mean(
                                data.astype(float),
                                parents_of, parent_indexes
                            )
                        )
                    else:
                        means = numpy.zeros((0,))
                else:
                    # No child measurements - all NaN
                    means = numpy.ones(len(parents_of)) * numpy.nan

                mean_feature_name = FF_MEAN % (self.sub_object_name.value, feature_name)

                m.add_measurement(self.parent_name.value, mean_feature_name, means)

        if self.show_window:
            workspace.display_data.parent_labels = parents.segmented

            workspace.display_data.parent_count = parents.count

            workspace.display_data.child_labels = children.segmented

            workspace.display_data.parents_of = parents_of