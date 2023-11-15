def add_ssh_scheme_to_git_uri(uri):
    """Cleans VCS uris from pipenv.patched.notpip format"""
    if isinstance(uri, six.string_types):
        # Add scheme for parsing purposes, this is also what pip does
        if uri.startswith("git+") and "://" not in uri:
            uri = uri.replace("git+", "git+ssh://", 1)
    return uri