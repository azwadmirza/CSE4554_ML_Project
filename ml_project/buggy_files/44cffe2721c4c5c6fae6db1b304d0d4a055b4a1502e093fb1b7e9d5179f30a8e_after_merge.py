    def from_dict(cls, d, app=None):
        options = d.copy()
        args, options['kwargs'] = cls._unpack_args(**options['kwargs'])
        return _upgrade(d, cls(*args, app=app, **options))