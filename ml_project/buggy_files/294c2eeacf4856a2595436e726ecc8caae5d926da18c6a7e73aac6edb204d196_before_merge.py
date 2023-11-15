    def __new__(cls, path, engine=None, **kwargs):
        # only switch class if generic(ExcelWriter)
        if cls == ExcelWriter:
            if engine is None:
                ext = os.path.splitext(path)[-1][1:]
                try:
                    engine = config.get_option('io.excel.%s.writer' % ext)
                except KeyError:
                    error = ValueError("No engine for filetype: '%s'" % ext)
                    raise error
            cls = get_writer(engine)

        return object.__new__(cls)