    def from_values(cls, val):
        """
        Returns a Layout given a list (or tuple) of viewable
        elements or just a single viewable element.
        """
        collection = isinstance(val, (list, tuple))
        if type(val) is cls:
            return val
        elif collection and len(val)>1:
            return cls._from_values(val)
        elif collection:
            val = val[0]
        return cls(items=[((sanitize_identifier(val.group),
                            sanitize_identifier(val.label if val.label else 'I')), val)])