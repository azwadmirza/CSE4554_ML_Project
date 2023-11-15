    def find_working_dir(self):
        # type: () -> Optional[str]
        view = self._current_view()
        window = view.window() if view else None

        if view and view.file_name():
            file_dir = os.path.dirname(view.file_name())
            if os.path.isdir(file_dir):
                return file_dir

        if window:
            folders = window.folders()
            if folders and os.path.isdir(folders[0]):
                return folders[0]

        return None