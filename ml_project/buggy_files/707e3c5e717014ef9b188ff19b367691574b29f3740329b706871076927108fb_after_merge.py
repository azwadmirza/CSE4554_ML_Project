    def format_yaml(self, value, flow_style=True):
        yaml_txt = salt.utils.yaml.safe_dump(
            value, default_flow_style=flow_style).strip()
        if yaml_txt.endswith(str('\n...')):  # future lint: disable=blacklisted-function
            yaml_txt = yaml_txt[:len(yaml_txt)-4]
        try:
            return Markup(yaml_txt)
        except UnicodeDecodeError:
            return Markup(salt.utils.stringutils.to_unicode(yaml_txt))