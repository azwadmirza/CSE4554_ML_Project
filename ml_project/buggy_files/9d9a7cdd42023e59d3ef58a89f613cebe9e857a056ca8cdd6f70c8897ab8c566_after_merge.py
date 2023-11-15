def minion_config(opts, vm_):
    '''
    Return a minion's configuration for the provided options and VM
    '''

    # Don't start with a copy of the default minion opts; they're not always
    # what we need. Some default options are Null, let's set a reasonable default
    minion = {
        'master': 'salt',
        'log_level': 'info',
        'hash_type': 'sha256',
    }

    # Now, let's update it to our needs
    minion['id'] = vm_['name']
    master_finger = salt.config.get_cloud_config_value('master_finger', vm_, opts)
    if master_finger is not None:
        minion['master_finger'] = master_finger
    minion.update(
        # Get ANY defined minion settings, merging data, in the following order
        # 1. VM config
        # 2. Profile config
        # 3. Global configuration
        salt.config.get_cloud_config_value(
            'minion', vm_, opts, default={}, search_global=True
        )
    )

    make_master = salt.config.get_cloud_config_value('make_master', vm_, opts)
    if 'master' not in minion and make_master is not True:
        raise SaltCloudConfigError(
            'A master setting was not defined in the minion\'s configuration.'
        )

    # Get ANY defined grains settings, merging data, in the following order
    # 1. VM config
    # 2. Profile config
    # 3. Global configuration
    minion.setdefault('grains', {}).update(
        salt.config.get_cloud_config_value(
            'grains', vm_, opts, default={}, search_global=True
        )
    )
    return minion