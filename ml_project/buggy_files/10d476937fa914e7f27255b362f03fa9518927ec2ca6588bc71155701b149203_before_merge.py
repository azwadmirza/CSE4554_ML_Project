def get_gke_clusters(container, project_id):
    """
    Returns a list of GKE clusters within some given project.

    :type container: The GCP Container resource object
    :param container: The Container resource object created by googleapiclient.discovery.build()

    :type project_id: str
    :param project_id: The Google Project Id that you are retrieving clusters from

    :rtype: Cluster Object
    :return: Cluster response object
    """
    try:
        req = container.projects().zones().clusters().list(projectId=project_id, zone='-')
        res = req.execute()
        return res
    except HttpError as e:
        reason = compute._get_error_reason(e)
        if reason == 'invalid':
            logger.warning(
                (
                    "The project %s is invalid - returned a 400 invalid error."
                    "Full details: %s"
                ),
                project_id,
                e,
            )
            return {}
        elif reason == 'forbidden':
            logger.warning(
                (
                    "You do not have container.projects.zones.clusters.list access to the project %s. "
                    "Full details: %s"
                ), project_id, e, )
            return {}
        else:
            raise