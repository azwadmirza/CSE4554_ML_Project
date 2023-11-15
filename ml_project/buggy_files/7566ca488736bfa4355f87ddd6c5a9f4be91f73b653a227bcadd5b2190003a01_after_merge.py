    def rglob(self, pattern, folder=False) -> Iterator[str]:
        if folder:
            return glob.iglob(f"{glob.escape(self.path)}{os.sep}**{os.sep}", recursive=True)
        else:
            return glob.iglob(
                f"{glob.escape(self.path)}{os.sep}**{os.sep}*{pattern}", recursive=True
            )