def list_deleted_vault_or_hsm(cmd, client, resource_type=None):
    if is_azure_stack_profile(cmd):
        return client.list_deleted()

    if resource_type is None:
        return client.list_deleted()

    if resource_type == 'hsm':
        raise InvalidArgumentValueError('Operation "list-deleted" has not been supported for HSM.')

    if resource_type == 'vault':
        return client.list_deleted()

    raise CLIError('Unsupported resource type: {}'.format(resource_type))