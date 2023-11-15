    def get_included_file_list(self):
        return [unicode(file_info["name"]) for file_info in self.current_download["files"] if file_info["included"]]