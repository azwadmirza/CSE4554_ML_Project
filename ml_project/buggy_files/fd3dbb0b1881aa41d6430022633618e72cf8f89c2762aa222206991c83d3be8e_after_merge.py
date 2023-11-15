    def get_object_relationships(self, pipeline):
        '''Return the object relationships produced by this module'''
        parent_name = self.x_name.value

        sub_object_name = self.y_name.value

        return [
            (
                cellprofiler.measurement.R_PARENT,
                parent_name,
                sub_object_name,
                cellprofiler.measurement.MCA_AVAILABLE_EACH_CYCLE
            ),
            (
                cellprofiler.measurement.R_CHILD,
                sub_object_name,
                parent_name,
                cellprofiler.measurement.MCA_AVAILABLE_EACH_CYCLE
            )
        ]