    def set_files(self, files):
        self.clear()
        self.files_data = []

        for file_info in files:
            if is_video_file(file_info['name']):
                self.addItem(file_info['name'])
                self.files_data.append(file_info)