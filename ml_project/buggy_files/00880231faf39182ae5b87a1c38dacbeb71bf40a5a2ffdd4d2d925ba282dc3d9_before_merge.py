def get_client(resource):
    resource_type = get_resource_type(resource)
    service = get_service_name(resource)
    if RESOURCE_TO_FUNCTION[resource_type][ACTION_CREATE].get('boto_client') == 'resource':
        return aws_stack.connect_to_resource(service)
    return aws_stack.connect_to_service(service)