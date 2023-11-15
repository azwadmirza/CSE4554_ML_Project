    def _get_defaults(self, args, default_values, kwo_defaults):
        if default_values:
            defaults = dict(zip(args[-len(default_values):], default_values))
        else:
            defaults = {}
        if kwo_defaults:
            defaults.update(kwo_defaults)
        return defaults