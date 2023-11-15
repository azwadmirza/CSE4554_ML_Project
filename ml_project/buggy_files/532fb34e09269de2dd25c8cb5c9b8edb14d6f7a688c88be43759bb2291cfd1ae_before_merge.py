def objective_fun(params):
    global task_id
    exp_prefix = params.pop("exp_prefix")
    exp_name = "{exp}_{pid}_{id}".format(
        exp=exp_prefix, pid=os.getpid(), id=task_id)
    max_retries = params.pop('max_retries', 0) + 1
    result_timeout = params.pop('result_timeout')
    run_experiment_kwargs = params.pop('run_experiment_kwargs', {})

    func, eval_func = _get_stubs(params)

    result_success = False
    while max_retries > 0:
        _launch_ec2(func, exp_prefix, exp_name, params, run_experiment_kwargs)
        task_id += 1
        max_retries -= 1
        if _wait_result(exp_prefix, exp_name, result_timeout):
            result_success = True
            break
        elif max_retries > 0:
            print("Timed out waiting for results. Retrying...")

    if not result_success:
        print("Reached max retries, no results. Giving up.")
        return {'status': STATUS_FAIL}

    print("Results in! Processing.")
    result_dict = eval_func(exp_prefix, exp_name)
    result_dict['status'] = STATUS_OK
    result_dict['params'] = params
    return result_dict