    def __init__(self, ignore_file_path, tree):
        assert os.path.isabs(ignore_file_path)

        self.ignore_file_path = ignore_file_path
        self.dirname = os.path.normpath(os.path.dirname(ignore_file_path))

        with tree.open(ignore_file_path, encoding="utf-8") as fobj:
            path_spec_lines = fobj.readlines()
            regex_pattern_list = map(
                GitWildMatchPattern.pattern_to_regex, path_spec_lines
            )
            self.ignore_spec = [
                (ignore, re.compile("|".join(item[0] for item in group)))
                for ignore, group in groupby(
                    regex_pattern_list, lambda x: x[1]
                )
            ]