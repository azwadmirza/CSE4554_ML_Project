    def format_yaml(self, value):
        return Markup(yaml.dump(value, default_flow_style=True).strip())