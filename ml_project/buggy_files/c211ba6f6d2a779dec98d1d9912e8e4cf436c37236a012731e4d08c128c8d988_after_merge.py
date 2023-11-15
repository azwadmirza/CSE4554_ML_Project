def _checksum_file_path(path):
    try:
        relpath = '.'.join((os.path.relpath(path, __opts__['cachedir']), 'hash'))
        if re.match(r'..[/\\]', relpath):
            # path is a local file
            relpath = salt.utils.path_join(
                'local',
                os.path.splitdrive(path)[-1].lstrip('/\\'),
            )
    except ValueError as exc:
        # The path is on a different drive (Windows)
        if str(exc).startswith('path is on'):
            drive, path = os.path.splitdrive(path)
            relpath = salt.utils.path_join(
                'local',
                drive.rstrip(':'),
                path.lstrip('/\\'),
            )
        elif str(exc).startswith('Cannot mix UNC'):
            relpath = salt.utils.path_join('unc', path)
        else:
            raise
    ret = salt.utils.path_join(__opts__['cachedir'], 'archive_hash', relpath)
    log.debug('Using checksum file %s for cached archive file %s', ret, path)
    return ret