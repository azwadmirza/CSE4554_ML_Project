def _smartos_zone_data():
    '''
    Return useful information from a SmartOS zone
    '''
    # Provides:
    #   zoneid
    #   zonename
    #   imageversion

    grains = {
        'zoneid': __salt__['cmd.run']('zoneadm list -p | awk -F: \'{ print $1 }\'', python_shell=True),
        'zonename': __salt__['cmd.run']('zonename'),
        'imageversion': 'Unknown',
    }

    imageversion = re.compile('Image:\\s(.+)')
    if os.path.isfile('/etc/product'):
        with salt.utils.files.fopen('/etc/product', 'r') as fp_:
            for line in fp_:
                line = salt.utils.stringutils.to_unicode(line)
                match = imageversion.match(line)
                if match:
                    grains['imageversion'] = match.group(1)

    return grains