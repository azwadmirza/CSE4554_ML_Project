def _groupname():
    '''
    Grain for the minion groupname
    '''
    if grp:
        groupname = grp.getgrgid(os.getgid()).gr_name
    else:
        groupname = ''

    return groupname