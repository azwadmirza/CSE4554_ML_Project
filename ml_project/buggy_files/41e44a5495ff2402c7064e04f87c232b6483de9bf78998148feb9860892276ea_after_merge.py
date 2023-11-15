def check_current_entry(module):
    # Check if entry exists, if not return False in exists in return dict,
    # if true return True and the entry in return dict
    existsdict = {'exist': False}
    lsitab = module.get_bin_path('lsitab')
    (rc, out, err) = module.run_command([lsitab, module.params['name']])
    if rc == 0:
        keys = ('name', 'runlevel', 'action', 'command')
        values = out.split(":")
        # strip non readable characters as \n
        values = map(lambda s: s.strip(), values)
        existsdict = dict(izip(keys, values))
        existsdict.update({'exist': True})
    return existsdict