def log_trial(args):
    ''''get trial log path'''
    trial_id_path_dict = {}
    trial_id_list = []
    nni_config = Config(get_config_filename(args))
    rest_port = nni_config.get_config('restServerPort')
    rest_pid = nni_config.get_config('restServerPid')
    if not detect_process(rest_pid):
        print_error('Experiment is not running...')
        return
    running, response = check_rest_server_quick(rest_port)
    if running:
        response = rest_get(trial_jobs_url(rest_port), REST_TIME_OUT)
        if response and check_response(response):
            content = json.loads(response.text)
            for trial in content:
                trial_id_list.append(trial.get('id'))
                if trial.get('logPath'):
                    trial_id_path_dict[trial.get('id')] = trial['logPath']
    else:
        print_error('Restful server is not running...')
        exit(1)
    if args.trial_id:
        if args.trial_id not in trial_id_list:
            print_error('Trial id {0} not correct, please check your command!'.format(args.trial_id))
            exit(1)
        if trial_id_path_dict.get(args.trial_id):
            print_normal('id:' + args.trial_id + ' path:' + trial_id_path_dict[args.trial_id])
        else:
            print_error('Log path is not available yet, please wait...')
            exit(1)
    else:
        print_normal('All of trial log info:')
        for key in trial_id_path_dict:
            print_normal('id:' + key + ' path:' + trial_id_path_dict[key])
        if not trial_id_path_dict:
            print_normal('None')