    def module_not_found(self, path: str, id: str, line: int, target: str) -> None:
        self.errors.set_file(path, id)
        stub_msg = "(Stub files are from https://github.com/python/typeshed)"
        if ((self.options.python_version[0] == 2 and moduleinfo.is_py2_std_lib_module(target)) or
                (self.options.python_version[0] >= 3 and
                 moduleinfo.is_py3_std_lib_module(target))):
            self.errors.report(
                line, 0, "No library stub file for standard library module '{}'".format(target))
            self.errors.report(line, 0, stub_msg, severity='note', only_once=True)
        elif moduleinfo.is_third_party_module(target):
            self.errors.report(line, 0, "No library stub file for module '{}'".format(target))
            self.errors.report(line, 0, stub_msg, severity='note', only_once=True)
        else:
            self.errors.report(line, 0, "Cannot find module named '{}'".format(target))
            self.errors.report(line, 0, '(Perhaps setting MYPYPATH '
                               'or using the "--ignore-missing-imports" flag would help)',
                               severity='note', only_once=True)