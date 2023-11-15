def envs():
    '''
    Return a list of refs that can be used as environments
    '''
    ret = set()
    repos = init()
    for repo in repos:
        repo.open()
        if __opts__['hgfs_branch_method'] != 'bookmarks':
            branches = repo.branches()
            for branch in branches:
                branch_name = branch[0]
                if branch_name == 'default':
                    branch_name = 'base'
                ret.add(branch_name)
        if __opts__['hgfs_branch_method'] != 'branches':
            bookmarks = repo.bookmarks()
            for bookmark in bookmarks:
                bookmark_name = bookmark[0]
                ret.add(bookmark_name)
        tags = repo.tags()
        for tag in tags:
            tag_name = tag[0]
            # Avoid adding the special 'tip' tag ad an env.
            if tag_name != 'tip':
                ret.add(tag_name)
    return list(ret)