    def on_rename(self):
        widget_item = self._get_current_treewidget_item()
        self.treeWidget.editItem(widget_item, 0)