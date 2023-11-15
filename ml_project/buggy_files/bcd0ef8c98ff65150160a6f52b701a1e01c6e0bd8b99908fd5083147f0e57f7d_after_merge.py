    def find_repo_path(self):
        # type: () -> Optional[str]
        """
        Similar to find_working_dir, except that it does not stop on the first
        directory found, rather on the first git repository found.
        """
        view = self._current_view()
        window = view.window() if view else None
        repo_path = None

        file_name = self._current_filename()
        if file_name:
            file_dir = os.path.dirname(file_name)
            if os.path.isdir(file_dir):
                repo_path = self._find_git_toplevel(file_dir)

        # fallback: use the first folder if the current file is not inside a git repo
        if not repo_path:
            if window:
                folders = window.folders()
                if folders and os.path.isdir(folders[0]):
                    repo_path = self._find_git_toplevel(folders[0])

        return os.path.realpath(repo_path) if repo_path else None