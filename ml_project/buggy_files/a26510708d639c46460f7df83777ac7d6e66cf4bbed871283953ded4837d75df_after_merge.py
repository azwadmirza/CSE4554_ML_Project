def check_experiment_status(wait=WAITING_TIME, max_retries=MAX_RETRIES):
    """Checks the status of the current experiment on the NNI REST endpoint
    Waits until the tuning has completed

    Args:
        wait (numeric) : time to wait in seconds
        max_retries (int): max number of retries
    """
    i = 0
    while i < max_retries:
        nni_status = get_experiment_status(NNI_STATUS_URL)
        if nni_status["status"] in ["DONE", "TUNER_NO_MORE_TRIAL"]:
            break
        elif nni_status["status"] not in ["RUNNING", "NO_MORE_TRIAL"]:
            raise RuntimeError("NNI experiment failed to complete with status {} - {}".format(nni_status["status"], 
                                                                                              nni_status["errors"][0]))
        time.sleep(wait)
        i += 1
    if i == max_retries:
        raise TimeoutError("check_experiment_status() timed out")