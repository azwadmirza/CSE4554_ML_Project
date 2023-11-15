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

    # NOTE: we are specifically interested in the SmartOS pkgsrc version and path
    #       - PKG_PATH MAY be different on non-SmartOS systems, but they will not
    #         use this grains module.
    #       - A sysadmin with advanced needs COULD create a 'spin' with a totally
    #         different URL. But at that point the value would be meaning less in
    #         the context of the pkgsrcversion grain as it will not followed the
    #         SmartOS pkgsrc versioning. So 'Unknown' would be appropriate.
    pkgsrcpath = re.compile('PKG_PATH=(.+)')
    pkgsrcversion = re.compile('^https?://pkgsrc.joyent.com/packages/SmartOS/(.+)/(.+)/All$')
    pkg_install_paths = [
        '/opt/local/etc/pkg_install.conf',
        '/opt/tools/etc/pkg_install.conf',
    ]
    for pkg_install in pkg_install_paths:
        if os.path.isfile(pkg_install):
            with salt.utils.files.fopen(pkg_install, 'r') as fp_:
                for line in fp_:
                    line = salt.utils.stringutils.to_unicode(line)
                    match_pkgsrcpath = pkgsrcpath.match(line)
                    if match_pkgsrcpath:
                        grains['pkgsrcpath'] = match_pkgsrcpath.group(1)
                        match_pkgsrcversion = pkgsrcversion.match(match_pkgsrcpath.group(1))
                        if match_pkgsrcversion:
                            grains['pkgsrcversion'] = match_pkgsrcversion.group(1)
                        break

    return grains