    def _ignore_details(self, path, is_dir):
        result = []
        for ignore, pattern in zip(self.regex_pattern_list, self.pattern_list):
            regex = re.compile(ignore[0])
            # skip system pattern
            if not pattern.file_info:
                continue
            if is_dir:
                path_dir = f"{path}/"
                if regex.match(path) or regex.match(path_dir):
                    result.append(pattern.file_info)
            else:
                if regex.match(path):
                    result.append(pattern.file_info)
        return result