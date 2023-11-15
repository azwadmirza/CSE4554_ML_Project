    def on_right_click_file_item(self, pos):
        num_selected = len(self.window().download_files_list.selectedItems())
        if num_selected == 0:
            return

        item_infos = []  # Array of (item, included, is_selected)
        selected_files_info = []

        for i in range(self.window().download_files_list.topLevelItemCount()):
            item = self.window().download_files_list.topLevelItem(i)
            is_selected = item in self.window().download_files_list.selectedItems()
            item_infos.append((item, item.file_info["included"], is_selected))

            if is_selected:
                selected_files_info.append(item.file_info)

        item_clicked = self.window().download_files_list.itemAt(pos)
        if not item_clicked or not item_clicked in self.window().download_files_list.selectedItems():
            return

        # Check whether we should enable the 'exclude' button
        num_excludes = 0
        num_includes_selected = 0
        for item_info in item_infos:
            if item_info[1] and item_info[0] in self.window().download_files_list.selectedItems():
                num_includes_selected += 1
            if not item_info[1]:
                num_excludes += 1

        menu = TriblerActionMenu(self)

        include_action = QAction('Include file' + ('(s)' if num_selected > 1 else ''), self)
        exclude_action = QAction('Exclude file' + ('(s)' if num_selected > 1 else ''), self)

        connect(include_action.triggered, lambda: self.on_files_included(selected_files_info))
        include_action.setEnabled(True)
        connect(exclude_action.triggered, lambda: self.on_files_excluded(selected_files_info))
        exclude_action.setEnabled(not (num_excludes + num_includes_selected == len(item_infos)))

        menu.addAction(include_action)
        menu.addAction(exclude_action)

        menu.exec_(self.window().download_files_list.mapToGlobal(pos))