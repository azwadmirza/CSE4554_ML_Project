def _fetch_project(uri, subdirectory, version, dst_dir, git_username, git_password):
    """
    Fetches the project from the uri. Makes sure the uri contains a valid MLproject file.
    Returns the working directory for running the project.
    """
    # Download a project to the target `dst_dir` from a Git URI or local path.
    if _GIT_URI_REGEX.match(uri):
        # Use Git to clone the project
        _fetch_git_repo(uri, version, dst_dir, git_username, git_password)
    else:
        if version is not None:
            raise ExecutionException("Setting a version is only supported for Git project URIs")
        # TODO: don't copy mlruns directory here
        # Note: uri might be equal to dst_dir, e.g. if we're not using a temporary work dir
        if uri != dst_dir:
            dir_util.copy_tree(src=uri, dst=dst_dir)

    # Make sure they don't have an outputs or mlruns directory (will need to change if we change
    # how we log results locally)
    shutil.rmtree(os.path.join(dst_dir, "outputs"), ignore_errors=True)
    shutil.rmtree(os.path.join(dst_dir, "mlruns"), ignore_errors=True)

    # Make sure there is a MLproject file in the specified working directory.
    if not os.path.isfile(os.path.join(dst_dir, subdirectory, "MLproject")):
        if subdirectory == '':
            raise ExecutionException("No MLproject file found in %s" % uri)
        else:
            raise ExecutionException("No MLproject file found in subdirectory %s of %s" %
                                     (subdirectory, uri))

    return os.path.join(dst_dir, subdirectory)