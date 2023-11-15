    def on_new_folder(self):
        parent_item = self._get_current_treewidget_item()
        self.__createFolder(parent_item)