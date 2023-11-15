        def _update(dict_, other):
            for key, value in other.items():
                if isinstance(dict_, list) and key.isdigit():
                    key = int(key)
                if isinstance(value, Mapping):
                    if isinstance(dict_, list):
                        fallback_value = dict_[key]
                    else:
                        fallback_value = dict_.get(key, {})
                    dict_[key] = _update(fallback_value, value)
                else:
                    dict_[key] = value
            return dict_