def _get_child(parent, collection_name, item_name, collection_key):
    if not item_name:
        raise CLIError("Name property for collection '{}' not provided. Check your input.".format(collection_name))
    items = getattr(parent, collection_name)
    result = next((x for x in items if getattr(x, collection_key, '').lower() == item_name.lower()), None)
    if not result:
        raise CLIError("Property '{}' does not exist for key '{}'.".format(item_name, collection_key))
    return result