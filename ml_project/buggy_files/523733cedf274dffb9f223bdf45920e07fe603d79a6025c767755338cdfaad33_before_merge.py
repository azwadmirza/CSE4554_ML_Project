    def get_child_measurement_columns(self, pipeline):
        columns = []
        if self.find_parent_child_distances in (D_BOTH, D_CENTROID):
            for parent_name in self.get_parent_names():
                columns += [
                    (self.sub_object_name.value, FF_CENTROID % parent_name, cellprofiler.measurement.COLTYPE_INTEGER)
                ]

        if self.find_parent_child_distances in (D_BOTH, D_MINIMUM):
            for parent_name in self.get_parent_names():
                columns += [
                    (self.sub_object_name.value, FF_MINIMUM % parent_name, cellprofiler.measurement.COLTYPE_INTEGER)
                ]

        return columns