    def _apply_free_defaults(self, defaults, overrides):
        consumed = []
        for override in overrides:
            key, value = override.split("=")
            if self.exists_in_search_path(key):
                # Do not add sweep configs into defaults, those will be added to the defaults
                # during sweep when after list is broken into items
                if "," not in value:
                    defaults.append({key: value})
                    consumed.append(override)

        return consumed