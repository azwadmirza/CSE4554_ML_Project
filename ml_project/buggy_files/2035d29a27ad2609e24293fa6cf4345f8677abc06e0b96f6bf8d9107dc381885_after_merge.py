    def get_parent_names(self):
        parent_names = [self.x_name.value]

        if self.wants_step_parent_distances.value:
            parent_names += [group.step_parent_name.value for group in self.step_parent_names]

        return parent_names