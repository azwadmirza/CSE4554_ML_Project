    def save_options(self, sender, args):
        self._config.halftone = self.halftone.IsChecked
        self._config.transparency = self.transparency.IsChecked
        self._config.proj_line_color = self.proj_line_color.IsChecked
        self._config.proj_line_pattern = self.proj_line_pattern.IsChecked
        self._config.proj_line_weight = self.proj_line_weight.IsChecked
        self._config.proj_fill_color = self.proj_fill_color.IsChecked
        self._config.proj_fill_pattern = self.proj_fill_pattern.IsChecked
        self._config.proj_fill_pattern_visibility = \
            self.proj_fill_pattern_visibility.IsChecked
        self._config.proj_bg_fill_color = self.proj_bg_fill_color.IsChecked
        self._config.proj_bg_fill_pattern = self.proj_bg_fill_pattern.IsChecked
        self._config.proj_bg_fill_pattern_visibility = \
            self.proj_bg_fill_pattern_visibility.IsChecked

        self._config.cut_line_color = self.cut_line_color.IsChecked
        self._config.cut_line_pattern = self.cut_line_pattern.IsChecked
        self._config.cut_line_weight = self.cut_line_weight.IsChecked
        self._config.cut_fill_color = self.cut_fill_color.IsChecked
        self._config.cut_fill_pattern = self.cut_fill_pattern.IsChecked
        self._config.cut_fill_pattern_visibility = \
            self.cut_fill_pattern_visibility.IsChecked
        self._config.cut_bg_fill_color = self.cut_bg_fill_color.IsChecked
        self._config.cut_bg_fill_pattern = self.cut_bg_fill_pattern.IsChecked
        self._config.cut_bg_fill_pattern_visibility = \
            self.cut_bg_fill_pattern_visibility.IsChecked

        self._config.dim_override = self.dim_override.IsChecked
        self._config.dim_textposition = self.dim_textposition.IsChecked
        self._config.dim_above = self.dim_above.IsChecked
        self._config.dim_below = self.dim_below.IsChecked
        self._config.dim_prefix = self.dim_prefix.IsChecked
        self._config.dim_suffix = self.dim_suffix.IsChecked

        script.save_config()
        self.Close()