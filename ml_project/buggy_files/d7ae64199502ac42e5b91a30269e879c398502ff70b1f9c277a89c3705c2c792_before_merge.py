def check_metrics_written(wait=WAITING_TIME, max_retries=MAX_RETRIES):
    """
    Waits until the metrics have been written to the trial logs
    """
    i = 0
    while i < max_retries:
        all_trials = requests.get(NNI_TRIAL_JOBS_URL).json()
        if all(['finalMetricData' in trial for trial in all_trials]):
            break
        time.sleep(wait)
        i += 1
    if i == max_retries:
        raise TimeoutError("check_metrics_written() timed out")