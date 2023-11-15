    def apply_modifier_info(self, origin, destination):
        o = getattr(origin, 'attrs', origin)
        d = getattr(destination, 'attrs', destination)
        for k in DATASET_KEYS:
            if k == 'modifiers':
                d[k] = self.attrs[k]
            elif d.get(k) is None:
                if self.attrs.get(k) is not None:
                    d[k] = self.attrs[k]
                elif o.get(k) is not None:
                    d[k] = o[k]