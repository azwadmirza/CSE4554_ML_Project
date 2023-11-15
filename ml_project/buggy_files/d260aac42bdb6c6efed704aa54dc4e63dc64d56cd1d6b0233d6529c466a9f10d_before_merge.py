    def format_json(self, value, sort_keys=True, indent=None):
        return Markup(salt.utils.json.dumps(value, sort_keys=sort_keys, indent=indent).strip())