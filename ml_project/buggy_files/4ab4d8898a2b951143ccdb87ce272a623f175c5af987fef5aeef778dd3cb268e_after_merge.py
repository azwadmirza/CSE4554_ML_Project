def get_url(path, repo=None, rev=None, remote=None):
    """
    Returns the URL to the storage location of a data file or directory tracked
    in a DVC repo. For Git repos, HEAD is used unless a rev argument is
    supplied. The default remote is tried unless a remote argument is supplied.

    Raises OutputNotFoundError if the file is not a dvc-tracked file.

    NOTE: This function does not check for the actual existence of the file or
    directory in the remote storage.
    """
    with _make_repo(repo, rev=rev) as _repo:
        path_info = PathInfo(_repo.root_dir) / path
        with reraise(FileNotFoundError, PathMissingError(path, repo)):
            metadata = _repo.repo_tree.metadata(path_info)

        if not metadata.is_dvc:
            raise OutputNotFoundError(path, repo)

        cloud = metadata.repo.cloud
        with _repo.state:
            hash_info = _repo.repo_tree.get_hash(path_info)
        return cloud.get_url_for(remote, checksum=hash_info.value)