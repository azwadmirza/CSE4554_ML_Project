    def paintEvent(self, event):
        # Paints the fold indicators and the possible fold region background
        # on the folding panel.
        super(FoldingPanel, self).paintEvent(event)
        painter = QPainter(self)
        # Draw background over the selected non collapsed fold region
        if self._mouse_over_line is not None:
            block = self.editor.document().findBlockByNumber(
                self._mouse_over_line)
            try:
                self._draw_fold_region_background(block, painter)
            except ValueError:
                pass
        # Draw fold triggers
        for top_position, line_number, block in self.editor.visible_blocks:
            if line_number in self.folding_regions:
                collapsed = self.folding_status[line_number]
                line_end = self.folding_regions[line_number]
                mouse_over = self._mouse_over_line == line_number
                self._draw_fold_indicator(
                    top_position, mouse_over, collapsed, painter)
                if collapsed:
                    # check if the block already has a decoration, it might
                    # have been folded by the parent editor/document in the
                    # case of cloned editor
                    for deco in self._block_decos:
                        if deco.block == block:
                            # no need to add a deco, just go to the next block
                            break
                    else:
                        self._add_fold_decoration(block, line_end)
                else:
                    for deco in self._block_decos:
                        # check if the block decoration has been removed, it
                        # might have been unfolded by the parent
                        # editor/document in the case of cloned editor
                        if deco.block == block:
                            # remove it and
                            self._block_decos.remove(deco)
                            self.editor.decorations.remove(deco)
                            del deco
                            break