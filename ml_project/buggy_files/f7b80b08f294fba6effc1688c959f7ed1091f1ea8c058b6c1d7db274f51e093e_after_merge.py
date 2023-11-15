    def _apply_defaults_overrides(overrides, defaults):
        consumed = []
        key_to_idx = {}
        for idx, d in enumerate(defaults):
            if isinstance(d, DictConfig):
                key = next(iter(d.keys()))
                key_to_idx[key] = idx
        for override in copy.deepcopy(overrides):
            key, value = override.split("=")
            if key in key_to_idx:
                # Do not add multirun configs into defaults, those will be added to the multirun config
                # after the list is broken into items
                if "," not in value:
                    if value == "null":
                        del defaults[key_to_idx[key]]
                    else:
                        defaults[key_to_idx[key]][key] = value
                overrides.remove(override)
                consumed.append(override)
        return consumed