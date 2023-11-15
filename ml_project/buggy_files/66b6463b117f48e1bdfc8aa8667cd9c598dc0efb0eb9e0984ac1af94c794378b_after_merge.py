    def get_match(self, abs_path):
        relative_path = relpath(abs_path, self.dirname)
        if os.name == "nt":
            relative_path = relative_path.replace("\\", "/")
        relative_path = cast_bytes(relative_path, "utf-8")

        for pattern in self.patterns:
            if match_pattern(
                relative_path, pattern
            ) and self._no_negate_pattern_matches(relative_path):
                return (abs_path, pattern, self.ignore_file_path)
        return None