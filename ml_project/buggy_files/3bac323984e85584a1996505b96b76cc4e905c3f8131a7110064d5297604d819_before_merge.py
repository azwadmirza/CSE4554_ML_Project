def launch_hyperopt_search(task_method,
                           eval_method,
                           param_space,
                           hyperopt_experiment_key,
                           hyperopt_db_host="localhost",
                           hyperopt_db_port=1234,
                           hyperopt_db_name="garage",
                           n_hyperopt_workers=1,
                           hyperopt_max_evals=100,
                           result_timeout=1200,
                           max_retries=0,
                           run_experiment_kwargs=None):
    """
    Launch a hyperopt search using EC2.

    This uses the hyperopt parallel processing functionality based on MongoDB.
    The MongoDB server at the specified host and port is assumed to be already
    running. Downloading and running MongoDB is pretty straightforward, see
    https://github.com/hyperopt/hyperopt/wiki/Parallelizing-Evaluations-During-
    Search-via-MongoDB for instructions.

    The parameter space to be searched over is specified in param_space. See
    https://github.com/hyperopt/hyperopt/wiki/FMin, section "Defining a search
    space" for further info. Also see the (very basic) example in
    contrib.rllab_hyperopt.example.main.py.

    NOTE: While the argument n_hyperopt_workers specifies the number of (local)
    parallel hyperopt workers to start, an equal number of EC2 instances will
    be started in parallel!

    NOTE2: garage currently terminates / starts a new EC2 instance for every
    task. This means what you'll pay amounts to hyperopt_max_evals *
    instance_hourly_rate. So you might want to be conservative with
    hyperopt_max_evals.

    :param task_method: the stubbed method call that runs the actual task.
     Should take a single dict as argument, with the params to evaluate.
     See e.g. contrib.rllab_hyperopt.example.task.py
    :param eval_method: the stubbed method call that reads in results returned
     from S3 and produces a score. Should take the exp_prefix and exp_name as
     arguments (this is where S3 results will be synced to).
     See e.g. contrib.rllab_hyperopt.example.score.py
    :param param_space: dict specifying the param space to search.
     See https://github.com/hyperopt/hyperopt/wiki/FMin, section
     "Defining a search space" for further info
    :param hyperopt_experiment_key: str, the key hyperopt will use to store
     results in the DB
    :param hyperopt_db_host: str, optional (default "localhost"). The host
     where mongodb runs
    :param hyperopt_db_port: int, optional (default 1234), the port where
     mongodb is listening for connections
    :param hyperopt_db_name: str, optional (default "garage"), the DB name
     where hyperopt will store results
    :param n_hyperopt_workers: int, optional (default 1). The nr of parallel
     workers to start. NOTE: an equal number of EC2 instances will be started
     in parallel.
    :param hyperopt_max_evals: int, optional (defailt 100). Number of
     parameterset evaluations hyperopt should try.
     NOTE: garage currently terminates / starts a new EC2 instance for every
     task. This means what you'll pay amounts to
     hyperopt_max_evals * instance_hourly_rate. So you might want to be
     conservative with hyperopt_max_evals.
    :param result_timeout: int, optional (default 1200). Nr of seconds to wait
     for results from S3 for a given task. If results are not in within this
     time frame, <max_retries> new attempts will be made. A new attempt entails
     launching the task again on a new EC2 instance.
    :param max_retries: int, optional (default 0). Number of times to retry
     launching a task when results don't come in from S3
    :param run_experiment_kwargs: dict, optional (default None). Further kwargs
     to pass to run_experiment. Note that specified values for exp_prefix,
     exp_name, variant, and confirm_remote will be ignored.
    :return the best result as found by hyperopt.fmin
    """
    exp_key = hyperopt_experiment_key

    worker_args = {
        'exp_prefix': exp_key,
        'task_module': task_method.__module__,
        'task_function': task_method.__name__,
        'eval_module': eval_method.__module__,
        'eval_function': eval_method.__name__,
        'result_timeout': result_timeout,
        'max_retries': max_retries
    }

    worker_args.update(param_space)
    if run_experiment_kwargs is not None:
        worker_args['run_experiment_kwargs'] = run_experiment_kwargs

    trials = MongoTrials(
        'mongo://{0}:{1:d}/{2}/jobs'.format(hyperopt_db_host, hyperopt_db_port,
                                            hyperopt_db_name),
        exp_key=exp_key)

    workers = _launch_workers(exp_key, n_hyperopt_workers, hyperopt_db_host,
                              hyperopt_db_port, hyperopt_db_name)

    s3sync = S3SyncThread()
    s3sync.start()

    print("Starting hyperopt")
    best = fmin(
        objective_fun,
        worker_args,
        trials=trials,
        algo=tpe.suggest,
        max_evals=hyperopt_max_evals)

    s3sync.stop()
    s3sync.join()

    for worker in workers:
        worker.terminate()

    return best