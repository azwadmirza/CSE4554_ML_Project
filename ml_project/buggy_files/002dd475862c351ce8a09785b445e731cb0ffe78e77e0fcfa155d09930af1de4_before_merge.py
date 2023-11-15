    def mouseMoveEvent(self, event):
        """
        Detect mouser over indicator and highlight the current scope in the
        editor (up and down decoration arround the foldable text when the mouse
        is over an indicator).

        :param event: event
        """
        super(FoldingPanel, self).mouseMoveEvent(event)
        th = TextHelper(self.editor)
        line = th.line_nbr_from_position(event.pos().y())
        if line >= 0:
            block = self.editor.document().findBlockByNumber(line)
            block = self.find_parent_scope(block)
            line_number = block.blockNumber()
            if line_number in self.folding_regions:
                if self._mouse_over_line is None:
                    # mouse enter fold scope
                    QApplication.setOverrideCursor(
                        QCursor(Qt.PointingHandCursor))
                if self._mouse_over_line != block.blockNumber() and \
                        self._mouse_over_line is not None:
                    # fold scope changed, a previous block was highlighter so
                    # we quickly update our highlighting
                    self._mouse_over_line = block.blockNumber()
                    self._highlight_block(block)
                else:
                    # same fold scope, request highlight
                    self._mouse_over_line = block.blockNumber()
                    self._highlight_runner.request_job(
                        self._highlight_block, block)
                self._highight_block = block
            else:
                # no fold scope to highlight, cancel any pending requests
                self._highlight_runner.cancel_requests()
                self._mouse_over_line = None
                QApplication.restoreOverrideCursor()
            self.repaint()