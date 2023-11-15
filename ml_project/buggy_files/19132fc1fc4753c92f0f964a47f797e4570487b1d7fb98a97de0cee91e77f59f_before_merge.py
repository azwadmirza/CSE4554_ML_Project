    def on_paste(self):
        parent_item = self.treeWidget.selectedItems()[0]
        parent = self.__extractData(parent_item)
        self.window().app.monitor.suspend()

        new_items = []
        for item in self.cutCopiedItems:
            if isinstance(item, model.Folder):
                new_item = ak_tree.FolderWidgetItem(parent_item, item)
                ak_tree.WidgetItemFactory.process_folder(new_item, item)
                parent.add_folder(item)
            elif isinstance(item, model.Phrase):
                new_item = ak_tree.PhraseWidgetItem(parent_item, item)
                parent.add_item(item)
            else:
                new_item = ak_tree.ScriptWidgetItem(parent_item, item)
                parent.add_item(item)

            item.persist()

            new_items.append(new_item)

        self.treeWidget.sortItems(0, Qt.AscendingOrder)
        self.treeWidget.setCurrentItem(new_items[-1])
        self.on_treeWidget_itemSelectionChanged()
        self.cutCopiedItems = []
        for item in new_items:
            item.setSelected(True)
        self.window().app.monitor.unsuspend()
        self.window().app.config_altered(False)