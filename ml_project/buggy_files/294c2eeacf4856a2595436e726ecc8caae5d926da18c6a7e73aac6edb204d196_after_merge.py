    def __new__(cls, path, engine=None, **kwargs):
        # only switch class if generic(ExcelWriter)
        if issubclass(cls, ExcelWriter):
            if engine is None:
                if isinstance(path, string_types):
                    ext = os.path.splitext(path)[-1][1:]
                else:
                    ext = 'xlsx'

                try:
                    engine = config.get_option('io.excel.%s.writer' % ext)
                except KeyError:
                    error = ValueError("No engine for filetype: '%s'" % ext)
                    raise error
            cls = get_writer(engine)

        return object.__new__(cls)