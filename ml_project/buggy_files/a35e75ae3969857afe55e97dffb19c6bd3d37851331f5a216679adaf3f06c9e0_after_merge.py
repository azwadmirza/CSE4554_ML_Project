    def is_tracked(self, path: str) -> bool:
        rel = PathInfo(path).relative_to(self.root_dir).as_posix().encode()
        rel_dir = rel + b"/"
        for path in self.repo.open_index():
            if path == rel or path.startswith(rel_dir):
                return True
        return False