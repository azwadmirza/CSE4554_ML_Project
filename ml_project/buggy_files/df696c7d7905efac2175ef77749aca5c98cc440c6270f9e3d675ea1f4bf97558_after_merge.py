    def _highlight_caret_scope(self):
        """
        Highlight the scope of the current caret position.

        This get called only if :attr:`
        spyder.widgets.panels.FoldingPanel.highlight_care_scope` is True.
        """
        cursor = self.editor.textCursor()
        block_nbr = cursor.blockNumber()
        if self._block_nbr != block_nbr:
            block = self.find_parent_scope(cursor.block())
            line_number = block.blockNumber()
            if line_number in self.folding_regions:
                self._mouse_over_line = block.blockNumber()
                try:
                    self._highlight_block(block)
                except KeyError:
                    # Catching the KeyError above is necessary to avoid
                    # issue spyder-ide/spyder#13230.
                    pass
            else:
                self._clear_scope_decos()
        self._block_nbr = block_nbr