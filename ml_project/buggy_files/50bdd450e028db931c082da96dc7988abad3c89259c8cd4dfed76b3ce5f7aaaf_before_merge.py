    def subfolders(self):
        files = list(self.multiglob(*[f"*{ext}" for ext in self._supported_music_ext]))
        folders = []
        for f in files:
            if f.exists() and f.parent not in folders and f.parent != self.localtrack_folder:
                folders.append(f.parent)
        return_folders = []
        for folder in folders:
            if folder.exists() and folder.is_dir():
                return_folders.append(LocalPath(str(folder.absolute())))
        return return_folders