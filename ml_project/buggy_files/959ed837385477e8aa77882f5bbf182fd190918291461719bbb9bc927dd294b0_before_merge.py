    def get_selected_file_path(self, base_dir: 'Optional[str]', index: int) -> str:
        file_path = self.reflist[index][0]
        if base_dir:
            file_path = os.path.join(base_dir, file_path)
        return file_path