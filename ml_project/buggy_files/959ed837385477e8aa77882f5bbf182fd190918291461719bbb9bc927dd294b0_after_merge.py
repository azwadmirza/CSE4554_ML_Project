    def get_selected_file_path(self, index: int) -> str:
        return self.get_full_path(self.reflist[index][0])