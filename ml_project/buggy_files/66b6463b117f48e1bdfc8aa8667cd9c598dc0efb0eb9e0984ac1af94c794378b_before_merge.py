    def get_match(self, abs_path):
        rel_path = os.path.relpath(abs_path, self.dirname)
        if os.name == "nt":
            rel_path = rel_path.replace("\\", "/")
        rel_path = cast_bytes(rel_path, "utf-8")

        for pattern in self.patterns:
            if match_pattern(
                rel_path, pattern
            ) and self._no_negate_pattern_matches(rel_path):
                return (abs_path, pattern, self.ignore_file_path)
        return None