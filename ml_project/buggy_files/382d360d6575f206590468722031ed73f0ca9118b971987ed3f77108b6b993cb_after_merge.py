def storage_blob_download_batch(client, source, destination, source_container_name, pattern=None, dryrun=False,
                                progress_callback=None, max_connections=2):
    def _download_blob(blob_service, container, destination_folder, blob_name):
        import os
        # TODO: try catch IO exception
        destination_path = os.path.join(destination_folder, blob_name)
        destination_folder = os.path.dirname(destination_path)
        if not os.path.exists(destination_folder):
            mkdir_p(destination_folder)

        blob = blob_service.get_blob_to_path(container, blob_name, destination_path, max_connections=max_connections,
                                             progress_callback=progress_callback)
        return blob.name

    source_blobs = list(collect_blobs(client, source_container_name, pattern))

    if dryrun:
        logger = get_logger(__name__)
        logger.warning('download action: from %s to %s', source, destination)
        logger.warning('    pattern %s', pattern)
        logger.warning('  container %s', source_container_name)
        logger.warning('      total %d', len(source_blobs))
        logger.warning(' operations')
        for b in source_blobs:
            logger.warning('  - %s', b)
        return []

    return list(_download_blob(client, source_container_name, destination, blob) for blob in source_blobs)