    def on_rename(self):
        widget_item = self.treeWidget.selectedItems()[0]
        self.treeWidget.editItem(widget_item, 0)