    def _get_attr_value(self, item, col):
        if not hasattr(item, col):
            # it's an inner obj attr
            try:
                return reduce(getattr, col.split('.'), item)
            except Exception as e:
                return ''
        if hasattr(getattr(item, col), '__call__'):
            # its a function
            return getattr(item, col)()
        else:
            # its an attribute
            value = getattr(item, col)
            # if value is an Enum instance than list and show widgets should display
            # its .value rather than its .name:
            if _has_enum and isinstance(value, enum.Enum):
                return value.value
            return value