    def update_folding(self, ranges):
        """Update folding panel folding ranges."""
        if ranges is None:
            return
        new_folding_ranges = {}
        for starting_line, ending_line in ranges:
            if ending_line > starting_line:
                new_folding_ranges[starting_line + 1] = ending_line + 1

        past_folding_regions = dict(self.folding_regions.copy())
        self.folding_regions = new_folding_ranges
        folding_status = {line: False for line in self.folding_regions}

        if len(folding_status) == len(self.folding_status):
            # No folding lines were introduced before/after
            self.folding_status = dict(
                zip(folding_status.keys(), self.folding_status.values()))
        else:
            # Line difference computation is done in order
            # to detect if folding regions were not modified.
            differ = self.editor.differ
            diff, previous_text = self.editor.text_diff
            current_text = self.editor.toPlainText()
            prev_offsets = self.__compute_line_offsets(previous_text)
            current_lines = self.__compute_line_offsets(current_text, True)

            for line in past_folding_regions:
                offset = prev_offsets.get(line)
                if offset:
                    new_offset = differ.diff_xIndex(diff, offset)
                    new_line = current_lines.get(new_offset)
                    if new_line and new_line in self.folding_regions:
                        try:
                            folding_status[new_line] = self.folding_status[line]
                        except KeyError:
                            pass
            self.folding_status = folding_status
        # Compute region nesting level
        self.folding_levels = {start_line: 0 for start_line in self.folding_regions}
        self.folding_nesting = {start_line: -1 for start_line in self.folding_regions}
        tree = IntervalTree.from_tuples(self.folding_regions.items())
        for (start, end) in self.folding_regions.items():
            nested_regions = tree.envelop(start, end)
            for region in nested_regions:
                if region.begin != start:
                    self.folding_levels[region.begin] += 1
                    self.folding_nesting[region.begin] = start
        self.update()