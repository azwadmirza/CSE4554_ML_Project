def _smartos_zone_pkgsrc_data():
    '''
    SmartOS zone pkgsrc information
    '''
    # Provides:
    #   pkgsrcversion
    #   pkgsrcpath

    grains = {
        'pkgsrcversion': 'Unknown',
        'pkgsrcpath': 'Unknown',
    }

    pkgsrcversion = re.compile('^release:\\s(.+)')
    if os.path.isfile('/etc/pkgsrc_version'):
        with salt.utils.files.fopen('/etc/pkgsrc_version', 'r') as fp_:
            for line in fp_:
                line = salt.utils.stringutils.to_unicode(line)
                match = pkgsrcversion.match(line)
                if match:
                    grains['pkgsrcversion'] = match.group(1)

    pkgsrcpath = re.compile('PKG_PATH=(.+)')
    if os.path.isfile('/opt/local/etc/pkg_install.conf'):
        with salt.utils.files.fopen('/opt/local/etc/pkg_install.conf', 'r') as fp_:
            for line in fp_:
                line = salt.utils.stringutils.to_unicode(line)
                match = pkgsrcpath.match(line)
                if match:
                    grains['pkgsrcpath'] = match.group(1)

    return grains