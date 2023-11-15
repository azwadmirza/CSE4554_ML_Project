    def get(self, item, default=None, *args, **kwargs):
        if item not in self:  # toggle case
            item = item.lower() if item.isupper() else upperfy(item)
        return super(DynaBox, self).get(item, default, *args, **kwargs)