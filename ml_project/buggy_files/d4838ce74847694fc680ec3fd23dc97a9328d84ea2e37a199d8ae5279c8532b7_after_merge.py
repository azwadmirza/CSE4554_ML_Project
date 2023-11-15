    def on_treeWidget_itemChanged(self, item, column):
        if item is self._get_current_treewidget_item() and column == 0:
            newText = str(item.text(0))
            if ui_common.validate(
                    not ui_common.EMPTY_FIELD_REGEX.match(newText),
                    "The name can't be empty.",
                    None,
                    self.window()):
                self.window().app.monitor.suspend()
                self.stack.currentWidget().set_item_title(newText)
                self.stack.currentWidget().rebuild_item_path()

                persistGlobal = self.stack.currentWidget().save()
                self.window().app.monitor.unsuspend()
                self.window().app.config_altered(persistGlobal)

                self.treeWidget.sortItems(0, Qt.AscendingOrder)
            else:
                item.update()