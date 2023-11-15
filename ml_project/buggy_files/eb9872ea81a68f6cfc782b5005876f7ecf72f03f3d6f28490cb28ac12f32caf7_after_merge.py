    def set_active_index(self, file_index):
        cur_ind = 0
        for ind, file_info in enumerate(self.files_data):
            if ind == file_index:
                self.item(cur_ind).setSelected(True)
                self.setFocus()
                break
            cur_ind += 1