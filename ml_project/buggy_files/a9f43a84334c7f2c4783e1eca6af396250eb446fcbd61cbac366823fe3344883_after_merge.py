def get_package_dir_permissions(spec):
    """Return the permissions configured for the spec.

    Include the GID bit if group permissions are on. This makes the group
    attribute sticky for the directory. Package-specific settings take
    precedent over settings for ``all``"""
    perms = get_package_permissions(spec)
    if perms & stat.S_IRWXG and spack.config.get('config:allow_sgid', True):
        perms |= stat.S_ISGID
    return perms