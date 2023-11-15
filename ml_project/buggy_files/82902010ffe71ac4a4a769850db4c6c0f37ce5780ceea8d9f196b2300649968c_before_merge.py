def _smartos_zone_pkgin_data():
    '''
    SmartOS zone pkgsrc information
    '''
    # Provides:
    #   pkgin_repositories

    grains = {
        'pkgin_repositories': [],
    }

    pkginrepo = re.compile('^(?:https|http|ftp|file)://.*$')
    if os.path.isfile('/opt/local/etc/pkgin/repositories.conf'):
        with salt.utils.files.fopen('/opt/local/etc/pkgin/repositories.conf', 'r') as fp_:
            for line in fp_:
                line = salt.utils.stringutils.to_unicode(line)
                if pkginrepo.match(line):
                    grains['pkgin_repositories'].append(line)

    return grains