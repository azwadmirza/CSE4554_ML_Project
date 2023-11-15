    def get_included_file_list(self):
        return [file_info["index"] for file_info in self.current_download["files"] if file_info["included"]]