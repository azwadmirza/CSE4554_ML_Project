    def get_namespace(resource_id):
        parsed = parse_resource_id(resource_id)
        if parsed.get('children'):
            return '/'.join([parsed.get('namespace'), parsed.get('type')])
        return parsed.get('namespace')