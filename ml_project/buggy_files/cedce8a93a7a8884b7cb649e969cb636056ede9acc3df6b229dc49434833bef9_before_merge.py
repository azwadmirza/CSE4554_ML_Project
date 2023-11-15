    def adjust_cells(self):
        """Adjust column size based on contents."""
        self.resizeColumnsToContents()
        fm = self.horizontalHeader().fontMetrics()
        names = [fm.width(s.cmd) for s in self.source_model.servers]
        self.setColumnWidth(CMD, max(names))
        self.horizontalHeader().setStretchLastSection(True)