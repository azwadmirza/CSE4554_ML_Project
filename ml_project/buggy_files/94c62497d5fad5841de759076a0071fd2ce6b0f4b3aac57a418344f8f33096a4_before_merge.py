def try_rebase(remote, branch):
    cmd = ['git', 'rev-list', '--max-count=1', '%s/%s' % (remote, branch)]
    p = sp.Popen(cmd, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    (rev, _) = p.communicate()
    if p.wait() != 0:
        return True
    cmd = ['git', 'update-ref', 'refs/heads/%s' % branch, rev.strip()]
    if sp.call(cmd) != 0:
        return False
    return True