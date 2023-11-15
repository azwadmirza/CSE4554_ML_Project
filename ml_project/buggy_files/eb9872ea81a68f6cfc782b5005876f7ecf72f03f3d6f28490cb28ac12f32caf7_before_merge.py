    def set_active_index(self, file_index):
        cur_ind = 0
        for index, _ in self.files_data:
            if index == file_index:
                self.item(cur_ind).setSelected(True)
                self.setFocus()
                break
            cur_ind += 1