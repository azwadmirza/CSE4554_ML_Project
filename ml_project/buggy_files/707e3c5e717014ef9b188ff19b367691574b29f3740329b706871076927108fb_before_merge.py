    def format_yaml(self, value, flow_style=True):
        yaml_txt = salt.utils.yaml.safe_dump(
            value, default_flow_style=flow_style).strip()
        if yaml_txt.endswith('\n...'):
            yaml_txt = yaml_txt[:len(yaml_txt)-4]
        return Markup(yaml_txt)