    def format_json(self, value, sort_keys=True, indent=None):
        json_txt = salt.utils.json.dumps(value, sort_keys=sort_keys, indent=indent).strip()
        try:
            return Markup(json_txt)
        except UnicodeDecodeError:
            return Markup(salt.utils.stringutils.to_unicode(json_txt))