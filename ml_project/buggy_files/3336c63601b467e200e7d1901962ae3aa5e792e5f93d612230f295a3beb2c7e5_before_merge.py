def storage_file_download_batch(cmd, client, source, destination, pattern=None, dryrun=False, validate_content=False,
                                max_connections=1, progress_callback=None, snapshot=None):
    """
    Download files from file share to local directory in batch
    """

    from azure.cli.command_modules.storage.util import glob_files_remotely, mkdir_p

    source_files = glob_files_remotely(cmd, client, source, pattern)

    if dryrun:
        source_files_list = list(source_files)

        logger = get_logger(__name__)
        logger.warning('download files from file share')
        logger.warning('    account %s', client.account_name)
        logger.warning('      share %s', source)
        logger.warning('destination %s', destination)
        logger.warning('    pattern %s', pattern)
        logger.warning('      total %d', len(source_files_list))
        logger.warning(' operations')
        for f in source_files_list:
            logger.warning('  - %s/%s => %s', f[0], f[1], os.path.join(destination, *f))

        return []

    def _download_action(pair):
        destination_dir = os.path.join(destination, pair[0])
        mkdir_p(destination_dir)

        get_file_args = {'share_name': source, 'directory_name': pair[0], 'file_name': pair[1],
                         'file_path': os.path.join(destination, *pair), 'max_connections': max_connections,
                         'progress_callback': progress_callback, 'snapshot': snapshot}

        if cmd.supported_api_version(min_api='2016-05-31'):
            get_file_args['validate_content'] = validate_content

        client.get_file_to_path(**get_file_args)
        return client.make_file_url(source, *pair)

    return list(_download_action(f) for f in source_files)