    def from_dict(cls, d, app=None):
        return _upgrade(
            d, group(d['kwargs']['tasks'], app=app, **d['options']),
        )