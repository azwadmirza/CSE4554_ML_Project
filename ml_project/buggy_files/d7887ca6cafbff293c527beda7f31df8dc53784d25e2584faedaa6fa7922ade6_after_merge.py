    def make_raw_parameters_from_file(cls, filepath):
        with open(filepath, 'r') as fh:
            try:
                ruamel_yaml = yaml_load(fh)
            except ScannerError as err:
                mark = err.problem_mark
                raise ConfigurationLoadError(
                    filepath,
                    "  reason: invalid yaml at line %(line)s, column %(column)s",
                    line=mark.line,
                    column=mark.column
                )
            except ReaderError as err:
                raise ConfigurationLoadError(filepath,
                                             "  reason: invalid yaml at position %(position)s",
                                             position=err.position)
            return cls.make_raw_parameters(filepath, ruamel_yaml) or EMPTY_MAP