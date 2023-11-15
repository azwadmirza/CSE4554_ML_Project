    def get_namespace(resource_id):
        parsed = parse_resource_id(resource_id)
        return parsed.get('namespace')