    def help_settings(self):
        help_settings = [
            self.x_name,
            self.y_name,
            self.method,
            self.image_name
        ]

        help_settings += self.apply_threshold.help_settings()[2:]

        help_settings += [
            self.distance_to_dilate,
            self.regularization_factor,
            self.fill_holes,
            self.wants_discard_edge,
            self.wants_discard_primary,
            self.new_primary_objects_name,
            self.wants_primary_outlines,
            self.new_primary_outlines_name,
            self.use_outlines,
            self.outlines_name
        ]