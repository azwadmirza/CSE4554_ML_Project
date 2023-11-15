    def _ignore_details(self, path, is_dir: bool):
        result = []
        for (regex, _), pattern_info in list(
            zip(self.regex_pattern_list, self.pattern_list)
        ):
            # skip system pattern
            if not pattern_info.file_info:
                continue

            regex = re.compile(regex)

            matches = bool(regex.match(path))
            if is_dir:
                matches |= bool(regex.match(f"{path}/"))

            if matches:
                result.append(pattern_info.file_info)

        return result