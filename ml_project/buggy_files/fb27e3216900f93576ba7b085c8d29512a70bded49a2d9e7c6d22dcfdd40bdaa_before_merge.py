    def apply_modifier_info(self, origin, destination):
        o = getattr(origin, 'info', origin)
        d = getattr(destination, 'info', destination)
        for k in DATASET_KEYS:
            if k == 'modifiers':
                d[k] = self.info[k]
            elif d.get(k) is None:
                if self.info.get(k) is not None:
                    d[k] = self.info[k]
                elif o.get(k) is not None:
                    d[k] = o[k]