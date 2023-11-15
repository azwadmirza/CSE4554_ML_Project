def merge_branch(repo, branch ):
    """try to merge the givent branch into the current one
    
    If something does not goes smoothly, merge is aborted
    
    Returns True if merge sucessfull, False otherwise
    """
    # Delete the branch first
    try :
        check_call(['git', 'pull', repo, branch], stdin=io.open(os.devnull))
    except CalledProcessError :
        check_call(['git', 'merge', '--abort'])
        return False
    return True