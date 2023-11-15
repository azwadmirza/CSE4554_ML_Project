    def _draw_collapsed_indicator(self, line_number, top_position, block,
                                  painter, mouse_hover=False):
        if line_number in self.folding_regions:
            collapsed = self.folding_status[line_number]
            line_end = self.folding_regions[line_number]
            mouse_over = self._mouse_over_line == line_number
            if not mouse_hover:
                self._draw_fold_indicator(
                    top_position, mouse_over, collapsed, painter)
            if collapsed:
                if mouse_hover:
                    self._draw_fold_indicator(
                        top_position, mouse_over, collapsed, painter)
                # check if the block already has a decoration,
                # it might have been folded by the parent
                # editor/document in the case of cloned editor
                for deco in self._block_decos:
                    if deco.block == block:
                        # no need to add a deco, just go to the
                        # next block
                        break
                else:
                    self._add_fold_decoration(block, line_end)
            elif not mouse_hover:
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