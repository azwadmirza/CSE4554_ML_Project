    def settings(self):
        settings = super(RelateObjects, self).settings()

        settings += [
            self.find_parent_child_distances,
            self.wants_per_parent_means,
            self.wants_step_parent_distances
        ]

        settings += [group.step_parent_name for group in self.step_parent_names]

        return settings