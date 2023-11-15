def is_profile_configured(opts, provider, profile_name, vm_=None):
    '''
    Check if the requested profile contains the minimum required parameters for
    a profile.

    Required parameters include image and provider for all drivers, while some
    drivers also require size keys.

    .. versionadded:: 2015.8.0
    '''
    # Standard dict keys required by all drivers.
    required_keys = ['provider']
    alias, driver = provider.split(':')

    # Most drivers need an image to be specified, but some do not.
    non_image_drivers = ['nova', 'virtualbox']

    # Most drivers need a size, but some do not.
    non_size_drivers = ['opennebula', 'parallels', 'proxmox', 'scaleway',
                        'softlayer', 'softlayer_hw', 'vmware', 'vsphere',
                        'virtualbox', 'profitbricks']

    provider_key = opts['providers'][alias][driver]
    profile_key = opts['providers'][alias][driver]['profiles'][profile_name]

    # If cloning on Linode, size and image are not necessary.
    # They are obtained from the to-be-cloned VM.
    if driver == 'linode' and profile_key.get('clonefrom', False):
        non_image_drivers.append('linode')
        non_size_drivers.append('linode')

    # If cloning on VMware, specifying image is not necessary.
    if driver == 'vmware' and 'image' not in list(profile_key.keys()):
        non_image_drivers.append('vmware')

    if driver not in non_image_drivers:
        required_keys.append('image')
        if driver == 'vmware':
            required_keys.append('datastore')
    elif driver in ['linode', 'virtualbox', 'vmware']:
        required_keys.append('clonefrom')
    elif driver == 'nova':
        nova_image_keys = ['image', 'block_device_mapping', 'block_device', 'boot_volume']
        if not any([key in provider_key for key in nova_image_keys]) and not any([key in profile_key for key in nova_image_keys]):
            required_keys.extend(nova_image_keys)

    if driver not in non_size_drivers:
        required_keys.append('size')

    # Check if required fields are supplied in the provider config. If they
    # are present, remove it from the required_keys list.
    for item in list(required_keys):
        if item in provider_key:
            required_keys.remove(item)

    # If a vm_ dict was passed in, use that information to get any other configs
    # that we might have missed thus far, such as a option provided in a map file.
    if vm_:
        for item in list(required_keys):
            if item in vm_:
                required_keys.remove(item)

    # Check for remaining required parameters in the profile config.
    for item in required_keys:
        if profile_key.get(item, None) is None:
            # There's at least one required configuration item which is not set.
            log.error(
                "The required '{0}' configuration setting is missing from "
                "the '{1}' profile, which is configured under the '{2}' "
                'alias.'.format(item, profile_name, alias)
            )
            return False

    return True