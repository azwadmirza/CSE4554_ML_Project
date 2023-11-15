def _get_snapshot_version_metadata_xml(artifactory_url, repository, group_id, artifact_id, version, headers):

    snapshot_version_metadata_url = _get_snapshot_version_metadata_url(
        artifactory_url=artifactory_url,
        repository=repository,
        group_id=group_id,
        artifact_id=artifact_id,
        version=version
    )

    try:
        request = urllib.request.Request(snapshot_version_metadata_url, None, headers)
        snapshot_version_metadata_xml = urllib.request.urlopen(request).read()
    except (HTTPError, URLError) as err:
        message = 'Could not fetch data from url: {0}. ERROR: {1}'.format(
            snapshot_version_metadata_url,
            err
        )
        raise CommandExecutionError(message)

    log.debug('snapshot_version_metadata_xml=%s', snapshot_version_metadata_xml)
    return snapshot_version_metadata_xml