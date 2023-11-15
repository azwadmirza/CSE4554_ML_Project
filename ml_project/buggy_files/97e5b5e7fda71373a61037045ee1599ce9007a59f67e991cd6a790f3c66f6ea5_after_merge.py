def _smartos_zone_data():
    '''
    Return useful information from a SmartOS zone
    '''
    # Provides:
    #   zoneid
    #   zonename
    #   imageversion
    grains = {}

    zoneinfo = __salt__['cmd.run']('zoneadm list -p').strip().split(":")
    grains["zoneid"] = zoneinfo[0]
    grains["zonename"] = zoneinfo[1]

    imageversion = re.compile('Image:\\s(.+)')
    grains["imageversion"] = "Unknown"
    if os.path.isfile('/etc/product'):
        with salt.utils.files.fopen('/etc/product', 'r') as fp_:
            for line in fp_:
                line = salt.utils.stringutils.to_unicode(line)
                match = imageversion.match(line)
                if match:
                    grains['imageversion'] = match.group(1)

    return grains