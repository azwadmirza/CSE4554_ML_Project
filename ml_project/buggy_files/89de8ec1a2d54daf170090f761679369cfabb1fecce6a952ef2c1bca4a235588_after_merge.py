    def on_files_excluded(self, *args):
        included_list = self.get_included_file_list()
        for file_data in self.selected_files_info:
            if file_data["index"] in included_list:
                included_list.remove(file_data["index"])

        self.set_included_files(included_list)