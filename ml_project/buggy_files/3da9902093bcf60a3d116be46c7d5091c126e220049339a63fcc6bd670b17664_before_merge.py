    def paintEvent(self, event):
        # Paints the fold indicators and the possible fold region background
        # on the folding panel.
        super(FoldingPanel, self).paintEvent(event)
        painter = QPainter(self)
        if not self._display_folding and not self._key_pressed:
            if any(self.folding_status.values()):
                for info in self.editor.visible_blocks:
                    top_position, line_number, block = info
                    self._draw_collapsed_indicator(
                        line_number, top_position, block,
                        painter, mouse_hover=True)
            return
        # Draw background over the selected non collapsed fold region
        if self._mouse_over_line is not None:
            block = self.editor.document().findBlockByNumber(
                self._mouse_over_line)
            try:
                self._draw_fold_region_background(block, painter)
            except (ValueError, KeyError):
                # Catching the KeyError above is necessary to avoid
                # issue spyder-ide/spyder#10918.
                # It happens when users have the mouse on top of the
                # folding panel and make some text modifications
                # that trigger a folding recomputation.
                pass
        # Draw fold triggers
        for top_position, line_number, block in self.editor.visible_blocks:
            self._draw_collapsed_indicator(
                line_number, top_position, block, painter, mouse_hover=False)