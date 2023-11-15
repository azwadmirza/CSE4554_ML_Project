    def source_strings_to_files(self, sources):
        results = []
        mesonlib.check_direntry_issues(sources)
        if not isinstance(sources, list):
            sources = [sources]
        for s in sources:
            if isinstance(s, (mesonlib.File, GeneratedListHolder,
                              TargetHolder, CustomTargetIndexHolder)):
                pass
            elif isinstance(s, str):
                self.validate_within_subproject(self.subdir, s)
                s = mesonlib.File.from_source_file(self.environment.source_dir, self.subdir, s)
            else:
                raise InterpreterException('Source item is {!r} instead of '
                                           'string or File-type object'.format(s))
            results.append(s)
        return results