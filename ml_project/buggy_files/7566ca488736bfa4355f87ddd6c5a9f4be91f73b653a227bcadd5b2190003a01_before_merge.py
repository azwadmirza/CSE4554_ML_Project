    def rglob(self, pattern, folder=False) -> Iterator[str]:
        if folder:
            return glob.iglob(f"{self.path}{os.sep}**{os.sep}", recursive=True)
        else:
            return glob.iglob(f"{self.path}{os.sep}**{os.sep}{pattern}", recursive=True)