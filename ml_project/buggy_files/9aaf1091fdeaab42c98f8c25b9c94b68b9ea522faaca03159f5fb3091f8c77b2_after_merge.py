def _sdc_mdata(mdata_list=None, mdata_get=None):
    '''
    SDC Metadata specified by there specs
    https://eng.joyent.com/mdata/datadict.html
    '''
    grains = {}
    sdc_text_keys = [
        'uuid',
        'server_uuid',
        'datacenter_name',
        'hostname',
        'dns_domain',
        'alias',
    ]
    sdc_json_keys = [
        'resolvers',
        'nics',
        'routes',
    ]

    if not mdata_list:
        mdata_list = salt.utils.path.which('mdata-list')

    if not mdata_get:
        mdata_get = salt.utils.path.which('mdata-get')

    if not mdata_list or not mdata_get:
        return grains

    for mdata_grain in sdc_text_keys+sdc_json_keys:
        mdata_value = __salt__['cmd.run']('{0} sdc:{1}'.format(mdata_get, mdata_grain), ignore_retcode=True)
        if mdata_value.startswith("ERROR:"):
            log.warning("unable to read sdc:{0} via mdata-get, mdata grain may be incomplete.".format(
                mdata_grain,
            ))
            continue

        if not mdata_value.startswith('No metadata for '):
            if 'mdata' not in grains:
                grains['mdata'] = {}
            if 'sdc' not in grains['mdata']:
                grains['mdata']['sdc'] = {}

            log.debug('found mdata entry sdc:%s with value %s', mdata_grain, mdata_value)
            mdata_grain = mdata_grain.replace('-', '_')
            mdata_grain = mdata_grain.replace(':', '_')
            if mdata_grain in sdc_json_keys:
                grains['mdata']['sdc'][mdata_grain] = salt.utils.json.loads(mdata_value)
            else:
                grains['mdata']['sdc'][mdata_grain] = mdata_value

    return grains