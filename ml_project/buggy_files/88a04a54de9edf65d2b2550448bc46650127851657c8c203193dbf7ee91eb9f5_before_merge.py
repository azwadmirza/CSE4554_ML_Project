def _filter_missing(repo, paths):
    repo_tree = RepoTree(repo, stream=True)
    for path in paths:
        metadata = repo_tree.metadata(path)
        if metadata.is_dvc:
            out = metadata.outs[0]
            if out.status()[str(out)] == "not in cache":
                yield path