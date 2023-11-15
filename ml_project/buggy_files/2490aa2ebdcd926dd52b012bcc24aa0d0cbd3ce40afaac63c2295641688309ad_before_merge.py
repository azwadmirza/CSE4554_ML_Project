    def format_yaml(obj):
        import yaml
        return yaml.safe_dump(obj.result, default_flow_style=False)