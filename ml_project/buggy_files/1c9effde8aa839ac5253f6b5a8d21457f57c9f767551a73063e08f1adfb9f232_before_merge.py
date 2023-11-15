    def file_renamed(self, editor, new_filename):
        """File was renamed, updating outline explorer tree"""
        editor_id = editor.get_id()
        if editor_id in list(self.editor_ids.values()):
            root_item = self.editor_items[editor_id]
            root_item.set_path(new_filename, fullpath=self.show_fullpath)
            self.__sort_toplevel_items()