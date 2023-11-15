    def on_new_folder(self):
        parent_item = self.treeWidget.selectedItems()[0]
        self.__createFolder(parent_item)