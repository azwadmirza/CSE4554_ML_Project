def _get_snapshot_url(artifactory_url, repository, group_id, artifact_id, version, packaging, snapshot_version=None, classifier=None, headers=None):
    if headers is None:
        headers = {}
    has_classifier = classifier is not None and classifier != ""

    if snapshot_version is None:
        try:
            snapshot_version_metadata = _get_snapshot_version_metadata(artifactory_url=artifactory_url, repository=repository, group_id=group_id, artifact_id=artifact_id, version=version, headers=headers)
            if packaging not in snapshot_version_metadata['snapshot_versions']:
                error_message = '''Cannot find requested packaging '{packaging}' in the snapshot version metadata.
                          artifactory_url: {artifactory_url}
                          repository: {repository}
                          group_id: {group_id}
                          artifact_id: {artifact_id}
                          packaging: {packaging}
                          classifier: {classifier}
                          version: {version}'''.format(
                            artifactory_url=artifactory_url,
                            repository=repository,
                            group_id=group_id,
                            artifact_id=artifact_id,
                            packaging=packaging,
                            classifier=classifier,
                            version=version)
                raise ArtifactoryError(error_message)

            if has_classifier and classifier not in snapshot_version_metadata['snapshot_versions']:
                error_message = '''Cannot find requested classifier '{classifier}' in the snapshot version metadata.
                          artifactory_url: {artifactory_url}
                          repository: {repository}
                          group_id: {group_id}
                          artifact_id: {artifact_id}
                          packaging: {packaging}
                          classifier: {classifier}
                          version: {version}'''.format(
                            artifactory_url=artifactory_url,
                            repository=repository,
                            group_id=group_id,
                            artifact_id=artifact_id,
                            packaging=packaging,
                            classifier=classifier,
                            version=version)
                raise ArtifactoryError(error_message)

            snapshot_version = snapshot_version_metadata['snapshot_versions'][packaging]
        except CommandExecutionError as err:
            log.error('Could not fetch maven-metadata.xml. Assuming snapshot_version=%s.', version)
            snapshot_version = version

    group_url = __get_group_id_subpath(group_id)

    file_name = '{artifact_id}-{snapshot_version}{classifier}.{packaging}'.format(
        artifact_id=artifact_id,
        snapshot_version=snapshot_version,
        packaging=packaging,
        classifier=__get_classifier_url(classifier))

    snapshot_url = '{artifactory_url}/{repository}/{group_url}/{artifact_id}/{version}/{file_name}'.format(
                        artifactory_url=artifactory_url,
                        repository=repository,
                        group_url=group_url,
                        artifact_id=artifact_id,
                        version=version,
                        file_name=file_name)
    log.debug('snapshot_url=%s', snapshot_url)

    return snapshot_url, file_name