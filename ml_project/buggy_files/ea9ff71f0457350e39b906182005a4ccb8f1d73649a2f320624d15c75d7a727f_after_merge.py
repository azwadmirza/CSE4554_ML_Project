    def find_working_dir(self):
        # type: () -> Optional[str]
        view = self._current_view()
        window = view.window() if view else None

        file_name = self._current_filename()
        if file_name:
            file_dir = os.path.dirname(file_name)
            if os.path.isdir(file_dir):
                return file_dir

        if window:
            folders = window.folders()
            if folders and os.path.isdir(folders[0]):
                return folders[0]

        return None