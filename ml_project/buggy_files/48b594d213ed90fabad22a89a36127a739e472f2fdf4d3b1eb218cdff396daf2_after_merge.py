    def glob(self, pattern, folder=False) -> Iterator[str]:
        if folder:
            return glob.iglob(f"{glob.escape(self.path)}{os.sep}*{os.sep}", recursive=False)
        else:
            return glob.iglob(f"{glob.escape(self.path)}{os.sep}*{pattern}", recursive=False)