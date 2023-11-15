    def from_dict(cls, d, app=None):
        args, d['kwargs'] = cls._unpack_args(**d['kwargs'])
        return _upgrade(d, cls(*args, app=app, **d))