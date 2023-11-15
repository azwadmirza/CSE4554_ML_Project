    def search(self, data, body):
        val = data.get(body.strip() if body else None, None)
        return (val is None
                or (self.config_get_bool("include_empty", True)
                    and val == ""))