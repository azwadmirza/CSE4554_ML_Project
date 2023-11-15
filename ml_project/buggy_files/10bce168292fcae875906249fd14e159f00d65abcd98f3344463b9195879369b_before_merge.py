    def __getattr__(self, name):
        setattr(Asty, name, lambda self, x, **kwargs: getattr(ast, name)(
            lineno=getattr(
                x, 'start_line', getattr(x, 'lineno', None)),
            col_offset=getattr(
                x, 'start_column', getattr(x, 'col_offset', None)),
            **kwargs))
        return getattr(self, name)