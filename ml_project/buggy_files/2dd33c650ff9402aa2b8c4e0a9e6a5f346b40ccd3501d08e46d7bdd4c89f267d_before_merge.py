    def _resize_columns(self):
        """Resize the completion columns based on column_widths."""
        width = self.size().width()
        column_widths = self.model().column_widths
        pixel_widths = [(width * perc // 100) for perc in column_widths]

        if self.verticalScrollBar().isVisible():
            delta = self.style().pixelMetric(QStyle.PM_ScrollBarExtent) + 5
            if pixel_widths[-1] > delta:
                pixel_widths[-1] -= delta
            else:
                pixel_widths[-2] -= delta
        for i, w in enumerate(pixel_widths):
            assert w >= 0, i
            self.setColumnWidth(i, w)