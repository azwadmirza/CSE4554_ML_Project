    def get_state(self):
        """
        Retrieve object state.
        """
        state = {}
        for attr, cls in self._stateobject_attributes.items():
            val = getattr(self, attr)
            if val is None:
                state[attr] = None
            elif hasattr(val, "get_state"):
                state[attr] = val.get_state()
            elif _is_list(cls):
                state[attr] = [x.get_state() for x in val]
            else:
                state[attr] = val
        return state