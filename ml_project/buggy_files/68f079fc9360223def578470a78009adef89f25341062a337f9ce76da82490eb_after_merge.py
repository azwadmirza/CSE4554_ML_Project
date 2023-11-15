def format_log(ret):
    '''
    Format the state into a log message
    '''
    msg = ''
    if isinstance(ret, dict):
        # Looks like the ret may be a valid state return
        if 'changes' in ret:
            # Yep, looks like a valid state return
            chg = ret['changes']
            if not chg:
                if ret['comment']:
                    msg = ret['comment']
                else:
                    msg = 'No changes made for {0[name]}'.format(ret)
            elif isinstance(chg, dict):
                if 'diff' in chg:
                    if isinstance(chg['diff'], string_types):
                        msg = 'File changed:\n{0}'.format(chg['diff'])
                if all([isinstance(x, dict) for x in chg.values()]):
                    if all([('old' in x and 'new' in x)
                            for x in chg.values()]):
                        # This is the return data from a package install
                        msg = 'Installed Packages:\n'
                        for pkg in chg:
                            old = chg[pkg]['old'] or 'absent'
                            new = chg[pkg]['new'] or 'absent'
                            msg += '{0!r} changed from {1!r} to ' \
                                   '{2!r}\n'.format(pkg, old, new)
            if not msg:
                msg = str(ret['changes'])
            if ret['result'] is True or ret['result'] is None:
                log.info(msg)
            else:
                log.error(msg)
    else:
        # catch unhandled data
        log.info(str(ret))