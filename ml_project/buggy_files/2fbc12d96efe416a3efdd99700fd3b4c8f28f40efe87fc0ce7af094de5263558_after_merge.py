def init():
    '''
    Return the git repo object for this session
    '''
    bp_ = os.path.join(__opts__['cachedir'], 'gitfs')
    repos = []
    for _, opt in enumerate(__opts__['gitfs_remotes']):
        repo_hash = hashlib.md5(opt).hexdigest()
        rp_ = os.path.join(bp_, repo_hash)
        if not os.path.isdir(rp_):
            os.makedirs(rp_)
        repo = git.Repo.init(rp_)
        if not repo.remotes:
            try:
                repo.create_remote('origin', opt)
            except Exception:
                # This exception occurs when two processes are trying to write
                # to the git config at once, go ahead and pass over it since
                # this is the only write
                # This should place a lock down
                pass
        if repo.remotes:
            repos.append(repo)
    return repos