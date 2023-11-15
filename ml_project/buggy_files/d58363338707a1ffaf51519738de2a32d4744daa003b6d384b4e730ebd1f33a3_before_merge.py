def _add_resource_group(obj):
    if isinstance(obj, list):
        for array_item in obj:
            _add_resource_group(array_item)
    elif isinstance(obj, dict):
        try:
            if 'resourceGroup' not in obj:
                if obj['id']:
                    obj['resourceGroup'] = _parse_id(obj['id'])['resource-group']
        except (KeyError, IndexError):
            pass
        for item_key in obj:
            _add_resource_group(obj[item_key])