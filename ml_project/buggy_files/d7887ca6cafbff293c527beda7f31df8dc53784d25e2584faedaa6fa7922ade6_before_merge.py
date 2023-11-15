    def make_raw_parameters_from_file(cls, filepath):
        with open(filepath, 'r') as fh:
            try:
                ruamel_yaml = yaml_load(fh)
            except ScannerError as err:
                mark = err.problem_mark
                raise LoadError("Invalid YAML", filepath, mark.line, mark.column)
        return cls.make_raw_parameters(filepath, ruamel_yaml) or EMPTY_MAP