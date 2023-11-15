def check_experiment_status(wait=WAITING_TIME, max_retries=MAX_RETRIES):
    """ Checks the status of the current experiment on the NNI REST endpoint
    Waits until the tuning has completed

    Args:
        wait (numeric) : time to wait in seconds
        max_retries (int): max number of retries
    """
    i = 0
    while i < max_retries:
        status = get_experiment_status(NNI_STATUS_URL)
        if status in ['DONE', 'TUNER_NO_MORE_TRIAL']:
            break
        elif status not in ['RUNNING', 'NO_MORE_TRIAL']:
            raise RuntimeError("NNI experiment failed to complete with status {}".format(status))
        time.sleep(wait)
        i += 1
    if i == max_retries:
        raise TimeoutError("check_experiment_status() timed out")