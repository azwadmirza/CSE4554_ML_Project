    def on_double_click(self, event):
        '''Handle double click event'''
        idx = self.get_mouse_idx(event)
        if idx == -1:
            return
        item, path_idx = self[idx]
        if item is None:
            return
        treeitem_x = self.get_treeitem_x()
        if path_idx is None:
            if event.GetX() < treeitem_x:
                # Handle second click on tree expand/contract as 
                # if the user clicked slowly
                #
                self.selections = set()
                item.opened = not item.opened
                self.schmutzy = True
                self.notify_selection_changed()
                self.Refresh(eraseBackground=False)
            return
        if self.fn_do_menu_command is not None:
            self.fn_do_menu_command([item.get_full_path(path_idx)], None)