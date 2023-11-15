def get_trials(optimize_mode):
    """Obtain information about the trials of the current experiment via the REST endpoint

    Args:
        optimize_mode (str): One of "minimize", "maximize". Determines how to obtain the best default metric.

    Returns:
         list: Trials info, list of (metrics, log path)
         dict: Metrics for the best choice of hyperparameters
         dict: Best hyperparameters
         str: Log path for the best trial
    """
    if optimize_mode not in ["minimize", "maximize"]:
        raise ValueError("optimize_mode should equal either minimize or maximize")
    all_trials = requests.get(NNI_TRIAL_JOBS_URL).json()
    trials = [(eval(trial["finalMetricData"][0]["data"]), trial["logPath"].split(":")[-1]) for trial in all_trials]
    sorted_trials = sorted(trials, key=lambda x: x[0]["default"], reverse=(optimize_mode == "maximize"))
    best_trial_path = sorted_trials[0][1]
    
    # Read the metrics from the trial directory in order to get the name of the default metric
    with open(os.path.join(best_trial_path, "metrics.json"), "r") as fp:
        best_metrics = json.load(fp)
    with open(os.path.join(best_trial_path, "parameter.cfg"), "r") as fp:
        best_params = json.load(fp)
    return trials, best_metrics, best_params, best_trial_path