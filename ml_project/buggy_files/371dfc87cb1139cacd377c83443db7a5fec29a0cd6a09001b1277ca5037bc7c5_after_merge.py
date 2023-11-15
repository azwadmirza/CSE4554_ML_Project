    def yield_renderers(self):
        """Use the rect glyphs to display the categorical heatmap.

        Takes reference points from data loaded at the ColumnDataSurce.
        """
        for group in self._data.groupby(**self.attributes):

            glyph = HeatmapGlyph(x=group.get_values(self.x.selection),
                                 y=group.get_values(self.y.selection),
                                 values=group.get_values(self.values.selection +
                                                         '_values'),
                                 width=self.bin_width * self.spacing_ratio,
                                 height=self.bin_height * self.spacing_ratio,
                                 line_color=group['color'],
                                 fill_color=group['color'],
                                 label=group.label)

            self.add_glyph(group, glyph)

            for renderer in glyph.renderers:
                yield renderer