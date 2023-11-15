def get_version(file, version=None):
    '''Determine current Leo version. Use git if in checkout, else internal Leo'''
    root = os.path.dirname(os.path.realpath(file))
    if os.path.exists(os.path.join(root,'.git')):
        version = git_version(file)
    else:
        version = get_semver(leoVersion.version)
    return version