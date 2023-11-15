    def validate_module(self, pipeline):
        '''Validate the module's settings

        Relate will complain if the children and parents are related
        by a prior module or if a step-parent is named twice'''
        for module in pipeline.modules():
            if module == self:
                break

            parent_features = module.get_measurements(pipeline, self.y_name.value, "Parent")

            if self.x_name.value in parent_features:
                raise cellprofiler.setting.ValidationError(
                    "{} and {} were related by the {} module".format(
                        self.y_name.value,
                        self.x_name.value,
                        module.module_name
                    ),
                    self.x_name
                )

        if self.has_step_parents and self.wants_step_parent_distances:
            step_parents = set()
            for group in self.step_parent_names:
                if group.step_parent_name.value in step_parents:
                    raise cellprofiler.setting.ValidationError(
                        u"{} has already been chosen".format(
                            group.step_parent_name.value
                        ),
                        group.step_parent_name
                    )

                step_parents.add(group.step_parent_name.value)