    def get_bindings_for(self, mode):
        """Get the combined bindings for the given mode."""
        bindings = dict(val.bindings.default[mode])
        for key, binding in val.bindings.commands[mode].items():
            if binding is None:
                bindings.pop(key, None)
            else:
                bindings[key] = binding
        return bindings