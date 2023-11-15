    def paintEvent(self, event):
        """Override Qt method."""
        painter = QPainter(self)

        color = QColor(self.color)
        color.setAlphaF(.5)
        painter.setPen(color)
        offset = self.editor.document().documentMargin() + \
            self.editor.contentOffset().x()
        folding_panel = self.editor.panels.get('FoldingPanel')
        folding_regions = folding_panel.folding_regions
        folding_status = folding_panel.folding_status
        leading_whitespaces = self.editor.leading_whitespaces
        for line_number in folding_regions:
            post_update = False
            end_line = folding_regions[line_number]
            start_block = self.editor.document().findBlockByNumber(
                line_number)
            end_block = self.editor.document().findBlockByNumber(end_line - 1)
            top = int(self.editor.blockBoundingGeometry(
                start_block).translated(self.editor.contentOffset()).top())
            bottom = int(self.editor.blockBoundingGeometry(
                end_block).translated(self.editor.contentOffset()).bottom())
            total_whitespace = leading_whitespaces[max(line_number - 1, 0)]
            end_whitespace = leading_whitespaces[end_line - 1]
            if end_whitespace != total_whitespace:
                x = (self.editor.fontMetrics().width(total_whitespace * '9') +
                     self.bar_offset + offset)
                painter.drawLine(x, top, x, bottom)