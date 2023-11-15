def _smartos_zone_pkgin_data():
    '''
    SmartOS zone pkgin information
    '''
    # Provides:
    #   pkgin_repositories

    grains = {
        'pkgin_repositories': [],
    }

    pkginrepo = re.compile('^(?:https|http|ftp|file)://.*$')
    repositories_path = [
        '/opt/local/etc/pkgin/repositories.conf',
        '/opt/tools/etc/pkgin/repositories.conf',
    ]
    for repositories in repositories_path:
        if os.path.isfile(repositories):
            with salt.utils.files.fopen(repositories, 'r') as fp_:
                for line in fp_:
                    line = salt.utils.stringutils.to_unicode(line).strip()
                    if pkginrepo.match(line):
                        grains['pkgin_repositories'].append(line)

    return grains