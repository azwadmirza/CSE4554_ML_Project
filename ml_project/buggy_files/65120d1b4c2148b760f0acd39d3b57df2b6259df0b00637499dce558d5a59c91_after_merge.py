def get_experiment_status(status_url=NNI_STATUS_URL):
    """Helper method. Gets the experiment status from the REST endpoint

    Args:
        status_url (str): URL for the REST endpoint

    Returns:
        dict: status of the experiment
    """
    return requests.get(status_url).json()