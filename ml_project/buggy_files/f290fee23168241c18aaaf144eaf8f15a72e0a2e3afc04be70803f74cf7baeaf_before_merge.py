    def _get_defaults(self, args, default_values, kwonlydefaults):
        if default_values:
            defaults = dict(zip(args[-len(default_values):], default_values))
        else:
            defaults = {}
        if kwonlydefaults:
            defaults.update(kwonlydefaults)
        return defaults