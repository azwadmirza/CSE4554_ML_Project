    def ignore(self, path, is_dir):
        def matches(pattern, path, is_dir) -> bool:
            matches_ = bool(pattern.match(path))

            if is_dir:
                matches_ |= bool(pattern.match(f"{path}/"))

            return matches_

        result = False

        for ignore, pattern in self.ignore_spec[::-1]:
            if matches(pattern, path, is_dir):
                result = ignore
                break
        return result