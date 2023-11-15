def _get_artifact_metadata_xml(artifactory_url, repository, group_id, artifact_id, headers):
    artifact_metadata_url = _get_artifact_metadata_url(artifactory_url=artifactory_url, repository=repository, group_id=group_id, artifact_id=artifact_id)
    try:
        request = urllib.request.Request(artifact_metadata_url, None, headers)
        artifact_metadata_xml = urllib.request.urlopen(request).read()
    except HTTPError as http_error:
        message = 'Could not fetch data from url: {url}, HTTPError: {error}'
        raise Exception(message.format(url=artifact_metadata_url, error=http_error))

    log.debug('artifact_metadata_xml=%s', artifact_metadata_xml)
    return artifact_metadata_xml