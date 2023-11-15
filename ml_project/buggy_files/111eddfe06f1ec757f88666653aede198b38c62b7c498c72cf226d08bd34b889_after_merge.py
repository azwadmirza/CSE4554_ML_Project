    def visible_settings(self):
        visible_settings = super(RelateObjects, self).visible_settings()

        visible_settings += [
            self.wants_per_parent_means,
            self.find_parent_child_distances
        ]

        if (self.find_parent_child_distances != D_NONE and self.has_step_parents):
            visible_settings += [self.wants_step_parent_distances]

            if self.wants_step_parent_distances:
                for group in self.step_parent_names:
                    visible_settings += group.visible_settings()

                visible_settings += [self.add_step_parent_button]

        return visible_settings