def _get_snapshot_version_metadata_xml(artifactory_url, repository, group_id, artifact_id, version, headers):
    snapshot_version_metadata_url = _get_snapshot_version_metadata_url(artifactory_url=artifactory_url, repository=repository, group_id=group_id, artifact_id=artifact_id, version=version)
    try:
        request = urllib.request.Request(snapshot_version_metadata_url, None, headers)
        snapshot_version_metadata_xml = urllib.request.urlopen(request).read()
    except HTTPError as http_error:
        message = 'Could not fetch data from url: {url}, HTTPError: {error}'
        raise Exception(message.format(url=snapshot_version_metadata_url, error=http_error))
    log.debug('snapshot_version_metadata_xml=%s', snapshot_version_metadata_xml)
    return snapshot_version_metadata_xml