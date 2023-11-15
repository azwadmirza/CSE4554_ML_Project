def acr_repository_delete(registry_name,
                          repository,
                          tag=None,
                          manifest=None,
                          resource_group_name=None,
                          username=None,
                          password=None,
                          yes=False):
    """Deletes a repository or a manifest/tag from the given repository in the specified container registry.
    :param str registry_name: The name of container registry
    :param str repository: The name of repository to delete
    :param str tag: The name of tag to delete
    :param str manifest: The sha256 based digest of manifest to delete
    :param str resource_group_name: The name of resource group
    :param str username: The username used to log into the container registry
    :param str password: The password used to log into the container registry
    """
    _, resource_group_name = validate_managed_registry(
        registry_name, resource_group_name, DELETE_NOT_SUPPORTED)

    login_server, username, password = get_access_credentials(
        registry_name=registry_name,
        resource_group_name=resource_group_name,
        username=username,
        password=password,
        repository=repository,
        permission='*')

    _INVALID = "Please specify either a tag name with --tag or a manifest digest with --manifest."

    # If manifest is not specified
    if manifest is None:
        if not tag:
            _user_confirmation("Are you sure you want to delete the repository '{}' "
                               "and all images under it?".format(repository), yes)
            path = '/v2/_acr/{}/repository'.format(repository)
        else:
            _user_confirmation("Are you sure you want to delete the tag '{}:{}'?".format(repository, tag), yes)
            path = '/v2/_acr/{}/tags/{}'.format(repository, tag)
    # If --manifest is specified as a flag
    elif not manifest:
        # Raise if --tag is empty
        if not tag:
            raise CLIError(_INVALID)
        manifest = _delete_manifest_confirmation(
            login_server=login_server,
            username=username,
            password=password,
            repository=repository,
            tag=tag,
            manifest=manifest,
            yes=yes)
        path = '/v2/{}/manifests/{}'.format(repository, manifest)
    # If --manifest is specified with a value
    else:
        # Raise if --tag is not empty
        if tag:
            raise CLIError(_INVALID)
        manifest = _delete_manifest_confirmation(
            login_server=login_server,
            username=username,
            password=password,
            repository=repository,
            tag=tag,
            manifest=manifest,
            yes=yes)
        path = '/v2/{}/manifests/{}'.format(repository, manifest)

    return _delete_data_from_registry(
        login_server=login_server,
        path=path,
        username=username,
        password=password)