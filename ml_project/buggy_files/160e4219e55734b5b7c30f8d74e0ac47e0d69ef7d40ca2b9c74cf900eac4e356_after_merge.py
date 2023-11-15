    def save_options(self, sender, args):
        # base
        self._config.halftone = self.halftone.IsChecked
        self._config.transparency = self.transparency.IsChecked

        # projection lines
        self._config.proj_line_color = self.proj_line_color.IsChecked
        self._config.proj_line_pattern = self.proj_line_pattern.IsChecked
        self._config.proj_line_weight = self.proj_line_weight.IsChecked

        # projection forground pattern
        self._config.proj_fill_color = self.proj_fill_color.IsChecked
        self._config.proj_fill_pattern = self.proj_fill_pattern.IsChecked
        self._config.proj_fill_pattern_visibility = \
            self.proj_fill_pattern_visibility.IsChecked

        # projection background pattern (Revit >= 2019)
        if HOST_APP.is_newer_than(2019, or_equal=True):
            self._config.proj_bg_fill_color = \
                self.proj_bg_fill_color.IsChecked
            self._config.proj_bg_fill_pattern = \
                self.proj_bg_fill_pattern.IsChecked
            self._config.proj_bg_fill_pattern_visibility = \
                self.proj_bg_fill_pattern_visibility.IsChecked

        # cut lines
        self._config.cut_line_color = self.cut_line_color.IsChecked
        self._config.cut_line_pattern = self.cut_line_pattern.IsChecked
        self._config.cut_line_weight = self.cut_line_weight.IsChecked

        # cut forground pattern
        self._config.cut_fill_color = self.cut_fill_color.IsChecked
        self._config.cut_fill_pattern = self.cut_fill_pattern.IsChecked
        self._config.cut_fill_pattern_visibility = \
            self.cut_fill_pattern_visibility.IsChecked

        # cut background pattern (Revit >= 2019)
        if HOST_APP.is_newer_than(2019, or_equal=True):
            self._config.cut_bg_fill_color = \
                self.cut_bg_fill_color.IsChecked
            self._config.cut_bg_fill_pattern = \
                self.cut_bg_fill_pattern.IsChecked
            self._config.cut_bg_fill_pattern_visibility = \
                self.cut_bg_fill_pattern_visibility.IsChecked

        # dim overrides
        self._config.dim_override = self.dim_override.IsChecked
        self._config.dim_textposition = self.dim_textposition.IsChecked
        self._config.dim_above = self.dim_above.IsChecked
        self._config.dim_below = self.dim_below.IsChecked
        self._config.dim_prefix = self.dim_prefix.IsChecked
        self._config.dim_suffix = self.dim_suffix.IsChecked

        script.save_config()
        self.Close()