def check_stopped(wait=WAITING_TIME, max_retries=MAX_RETRIES):
    """
    Checks that there is no NNI experiment active (the URL is not accessible)
    This method should be called after 'nnictl stop' for verification

    Args:
        wait (numeric) : time to wait in seconds
        max_retries (int): max number of retries
    """
    i = 0
    while i < max_retries:
        try:
            get_experiment_status(NNI_STATUS_URL)
        except:
            break
        time.sleep(wait)
        i += 1
    if i == max_retries:
        raise TimeoutError("check_stopped() timed out")