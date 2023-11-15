def _groupname():
    '''
    Grain for the minion groupname
    '''
    if grp:
        try:
            groupname = grp.getgrgid(os.getgid()).gr_name
        except KeyError:
            groupname = ''
    else:
        groupname = ''

    return groupname