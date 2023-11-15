    def get_step_parents(self, pipeline):
        '''Return the possible step-parents associated with the parent'''
        step_parents = set()

        parent_name = self.parent_name.value

        for module in pipeline.modules():
            if module.module_num == self.module_num:
                return list(step_parents)

            # Objects that are the parent of the parents
            grandparents = module.get_measurements(
                pipeline,
                parent_name,
                cellprofiler.measurement.C_PARENT
            )

            step_parents.update(grandparents)

            # Objects that are the children of the parents
            siblings = module.get_measurements(
                pipeline,
                parent_name,
                cellprofiler.measurement.C_CHILDREN
            )

            for sibling in siblings:
                match = re.match("^([^_]+)_Count", sibling)

                if match is not None:
                    sibling_name = match.groups()[0]

                    if parent_name in module.get_measurements(
                            pipeline,
                            sibling_name,
                            cellprofiler.measurement.C_PARENT
                    ):
                        step_parents.add(sibling_name)

        return list(step_parents)