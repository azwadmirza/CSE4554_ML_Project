    def _handle_result(self, result):
        config_update = result.get("config", {}).copy()
        log = {}
        flat_result = flatten_dict(result, delimiter="/")

        for k, v in flat_result.items():
            if any(
                    k.startswith(item + "/") or k == item
                    for item in self._to_config):
                config_update[k] = v
            elif any(
                    k.startswith(item + "/") or k == item
                    for item in self._exclude):
                continue
            elif not isinstance(v, Number):
                continue
            else:
                log[k] = v

        config_update.pop("callbacks", None)  # Remove callbacks
        return log, config_update