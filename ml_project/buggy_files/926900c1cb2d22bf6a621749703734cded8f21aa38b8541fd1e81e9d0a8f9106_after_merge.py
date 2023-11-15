def process_public_ip_create_namespace(cmd, namespace):
    get_default_location_from_resource_group(cmd, namespace)
    validate_public_ip_prefix(cmd, namespace)
    validate_ip_tags(cmd, namespace)
    validate_tags(namespace)