    def from_dict(cls, d, **kwargs):
        args = []
        for k in DATASET_KEYS:
            val = kwargs.get(k, d.get(k))
            # force modifiers to tuple
            if k == 'modifiers' and val is not None:
                val = tuple(val)
            args.append(val)

        return cls(*args)