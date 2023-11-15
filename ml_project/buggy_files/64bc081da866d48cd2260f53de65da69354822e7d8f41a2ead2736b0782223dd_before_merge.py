    def _subplot_label(self, axis):
        layout_num = self.layout_num if self.subplot else 1
        if self.sublabel_format and not self.adjoined and layout_num > 0:
            from mpl_toolkits.axes_grid1.anchored_artists import AnchoredText
            labels = {}
            if '{Alpha}' in self.sublabel_format:
                labels['Alpha'] = int_to_alpha(layout_num-1)
            elif '{alpha}' in self.sublabel_format:
                labels['alpha'] = int_to_alpha(layout_num-1, upper=False)
            elif '{numeric}' in self.sublabel_format:
                labels['numeric'] = self.layout_num
            elif '{Roman}' in self.sublabel_format:
                labels['Roman'] = int_to_roman(layout_num)
            elif '{roman}' in self.sublabel_format:
                labels['roman'] = int_to_roman(layout_num).lower()
            at = AnchoredText(self.sublabel_format.format(**labels), loc=3,
                              bbox_to_anchor=self.sublabel_position, frameon=False,
                              prop=dict(size=self.sublabel_size, weight='bold'),
                              bbox_transform=axis.transAxes)
            at.patch.set_visible(False)
            axis.add_artist(at)
            sublabel = at.txt.get_children()[0]
            self.handles['sublabel'] = sublabel
            self.handles['bbox_extra_artists'] += [sublabel]