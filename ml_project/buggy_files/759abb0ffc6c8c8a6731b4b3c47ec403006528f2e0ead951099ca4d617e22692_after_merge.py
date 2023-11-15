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
            elif isinstance(val, dict):
                s = {}
                for k, v in val.items():
                    if hasattr(v, "get_state"):
                        s[k] = v.get_state()
                    else:
                        s[k] = v
                state[attr] = s
            else:
                state[attr] = val
        return state