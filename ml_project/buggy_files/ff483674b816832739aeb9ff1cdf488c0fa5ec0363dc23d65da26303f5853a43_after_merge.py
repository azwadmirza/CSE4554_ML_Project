    def subfolders_in_tree(self):
        files = list(self.multirglob(*[f"*{ext}" for ext in self._all_music_ext]))
        folders = []
        for f in files:
            if f.exists() and f.parent not in folders and f.parent != self.localtrack_folder:
                folders.append(f.parent)
        return_folders = []
        for folder in folders:
            if folder.exists() and folder.is_dir():
                return_folders.append(LocalPath(str(folder.absolute())))
        return sorted(return_folders, key=lambda x: x.to_string_user().lower())