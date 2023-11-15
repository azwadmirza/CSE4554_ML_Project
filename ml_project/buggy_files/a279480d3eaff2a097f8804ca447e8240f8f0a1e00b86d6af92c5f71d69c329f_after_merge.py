def _get_artifact_metadata_xml(artifactory_url, repository, group_id, artifact_id, headers):

    artifact_metadata_url = _get_artifact_metadata_url(
        artifactory_url=artifactory_url,
        repository=repository,
        group_id=group_id,
        artifact_id=artifact_id
    )

    try:
        request = urllib.request.Request(artifact_metadata_url, None, headers)
        artifact_metadata_xml = urllib.request.urlopen(request).read()
    except (HTTPError, URLError) as err:
        message = 'Could not fetch data from url: {0}. ERROR: {1}'.format(
            artifact_metadata_url,
            err
        )
        raise CommandExecutionError(message)

    log.debug('artifact_metadata_xml=%s', artifact_metadata_xml)
    return artifact_metadata_xml