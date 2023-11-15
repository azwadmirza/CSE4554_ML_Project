        def _update(dict_, other):
            for key, value in other.items():
                if isinstance(value, Mapping):
                    dict_[key] = _update(dict_.get(key, {}), value)
                else:
                    dict_[key] = value
            return dict_