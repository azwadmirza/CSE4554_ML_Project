    def get_subpaths(self, basepath):
        """Returns direct subpaths for this object, i.e. either the named subfolder or all
        subfolders matching the pattern"""
        if isinstance(self.pattern, Pattern):
            return (os.path.join(basepath, p) for p in os.listdir(basepath)
                    if self.pattern.match(p) and os.path.isdir(os.path.join(basepath, p)))
        else:
            path = os.path.join(basepath, self.pattern)
            return [path] if os.path.isdir(path) else []