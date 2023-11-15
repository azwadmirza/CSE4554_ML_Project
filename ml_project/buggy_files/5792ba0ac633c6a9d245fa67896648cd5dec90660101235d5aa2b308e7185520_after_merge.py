    def on_files_included(self, files_data):
        included_list = self.get_included_file_list()
        for file_data in files_data:
            if not file_data["index"] in included_list:
                included_list.append(file_data["index"])

        self.set_included_files(included_list)