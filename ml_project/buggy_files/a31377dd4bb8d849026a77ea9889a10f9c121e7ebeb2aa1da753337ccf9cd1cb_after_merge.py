def uri_to_resource(resource_file):
    # ## Returns the URI for a resource
    # The basic case is that the resource is on saltstack.com
    # It could be the case that the resource is cached.
    salt_uri = 'https://repo.saltstack.com/windows/dependencies/' + resource_file
    if os.getenv('SALTREPO_LOCAL_CACHE') is None:
        # if environment variable not set, return the basic case
        return salt_uri
    if not os.path.isdir(os.getenv('SALTREPO_LOCAL_CACHE')):
        # if environment variable is not a directory, return the basic case
        return salt_uri
    cached_resource = os.path.join(os.getenv('SALTREPO_LOCAL_CACHE'), resource_file)
    cached_resource = cached_resource.replace('/', '\\')
    if not os.path.isfile(cached_resource):
        # if file does not exist, return the basic case
        return salt_uri
    if os.path.getsize(cached_resource) == 0:
        # if file has zero size, return the basic case
        return salt_uri
    return cached_resource