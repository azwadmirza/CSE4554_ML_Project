def get_experiment_status(status_url):
    """
    Helper method. Gets the experiment status from the REST endpoint

    Args:
        status_url (str): URL for the REST endpoint

    Returns:
        str: status of the experiment
    """
    nni_status = requests.get(status_url).json()
    return nni_status['status']