    def _apply_free_defaults(self, defaults, overrides):
        consumed = []
        for override in overrides:
            key, value = override.split("=")
            if self.exists_in_search_path(key):
                # Do not add multirun configs into defaults, those will be added to the defaults
                # during the runs after list is broken into items
                if "," not in value:
                    defaults.append({key: value})
                overrides.remove(override)
                consumed.append(override)

        return consumed