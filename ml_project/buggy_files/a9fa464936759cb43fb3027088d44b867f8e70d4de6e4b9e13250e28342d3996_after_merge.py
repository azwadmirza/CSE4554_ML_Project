def mod_data(opts):
    '''
    Generate the module arguments for the shim data
    '''
    # TODO, change out for a fileserver backend
    sync_refs = [
            'modules',
            'states',
            'grains',
            'renderers',
            'returners',
            ]
    ret = {}
    for env in opts['file_roots']:
        for path in opts['file_roots'][env]:
            for ref in sync_refs:
                mod_str = ''
                pl_dir = os.path.join(path, '_{0}'.format(ref))
                if os.path.isdir(pl_dir):
                    for fn_ in os.listdir(pl_dir):
                        if not os.path.isfile(fn_):
                            continue
                        mod_path = os.path.join(pl_dir, fn_)
                        with open(mod_path) as fp_:
                            code_str = fp_.read().encode('base64')
                        mod_str += '{0}|{1},'.format(fn_, code_str)
                mod_str = mod_str.rstrip(',')
                ret[ref] = mod_str
    return ret