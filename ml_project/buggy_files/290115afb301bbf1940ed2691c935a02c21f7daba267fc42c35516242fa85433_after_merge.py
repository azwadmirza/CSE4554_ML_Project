        def matches(pattern, path, is_dir) -> bool:
            matches_ = bool(pattern.match(path))

            if is_dir:
                matches_ |= bool(pattern.match(f"{path}/"))

            return matches_