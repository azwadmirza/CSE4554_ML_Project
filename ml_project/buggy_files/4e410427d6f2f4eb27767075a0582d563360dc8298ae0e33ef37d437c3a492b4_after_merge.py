    def on_save(self):
        logger.info("User requested file save.")
        if self.stack.currentWidget().validate():
            self.window().app.monitor.suspend()
            persist_global = self.stack.currentWidget().save()
            self.window().save_completed(persist_global)
            self.set_dirty(False)
            item = self._get_current_treewidget_item()
            item.update()
            self.treeWidget.update()
            self.treeWidget.sortItems(0, Qt.AscendingOrder)
            self.window().app.monitor.unsuspend()
            return False

        return True