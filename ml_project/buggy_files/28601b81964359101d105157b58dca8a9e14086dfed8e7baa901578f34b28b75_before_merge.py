    def get(self, item, default=None, *args, **kwargs):
        value = super(DynaBox, self).get(item, default, *args, **kwargs)
        if value is None or value == default:
            n_item = item.lower() if item.isupper() else upperfy(item)
            value = super(DynaBox, self).get(n_item, default, *args, **kwargs)
        return value