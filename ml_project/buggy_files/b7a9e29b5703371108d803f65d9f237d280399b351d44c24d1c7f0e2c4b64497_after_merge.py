    def get(self, item, default=None, *args, **kwargs):
        if item not in self:  # toggle case
            item = item.lower() if item.isupper() else upperfy(item)
        value = super(DynaBox, self).get(item, empty, *args, **kwargs)
        if value is empty:
            # see Issue: #486
            return self._case_insensitive_get(item, default)
        return value