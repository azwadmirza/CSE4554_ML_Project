def call_fun(func, config_data, dsl_path, config_path):
    ip = server_conf.get(SERVERS).get(ROLE).get('host')
    if ip in ['localhost', '127.0.0.1']:
        ip = get_lan_ip()
    http_port = server_conf.get(SERVERS).get(ROLE).get('http.port')
    server_url = "http://{}:{}/{}".format(ip, http_port, API_VERSION)

    if func in JOB_OPERATE_FUNC:
        if func == 'submit_job':
            if not config_path:
                raise Exception('the following arguments are required: {}'.format('runtime conf path'))
            dsl_data = {}
            if dsl_path or config_data.get('job_parameters', {}).get('job_type', '') == 'predict':
                if dsl_path:
                    dsl_path = os.path.abspath(dsl_path)
                    with open(dsl_path, 'r') as f:
                        dsl_data = json.load(f)
            else:
                raise Exception('the following arguments are required: {}'.format('dsl path'))
            post_data = {'job_dsl': dsl_data,
                         'job_runtime_conf': config_data}
            response = requests.post("/".join([server_url, "job", func.rstrip('_job')]), json=post_data)
            if response.json()['retcode'] == 999:
                print('use service.sh to start standalone node server....')
                os.system('sh service.sh start --standalone_node')
                time.sleep(5)
                response = requests.post("/".join([server_url, "job", func.rstrip('_job')]), json=post_data)
        else:
            if func != 'query_job':
                detect_utils.check_config(config=config_data, required_arguments=['job_id'])
            post_data = config_data
            response = requests.post("/".join([server_url, "job", func.rstrip('_job')]), json=post_data)
            if func == 'query_job':
                response = response.json()
                if response['retcode'] == 0:
                    for i in range(len(response['data'])):
                        del response['data'][i]['f_runtime_conf']
                        del response['data'][i]['f_dsl']
    elif func in JOB_FUNC:
        if func == 'job_config':
            detect_utils.check_config(config=config_data, required_arguments=['job_id', 'role', 'party_id', 'output_path'])
            response = requests.post("/".join([server_url, func.replace('_', '/')]), json=config_data)
            response_data = response.json()
            if response_data['retcode'] == 0:
                job_id = response_data['data']['job_id']
                download_directory = os.path.join(config_data['output_path'], 'job_{}_config'.format(job_id))
                os.makedirs(download_directory, exist_ok=True)
                for k, v in response_data['data'].items():
                    if k == 'job_id':
                        continue
                    with open('{}/{}.json'.format(download_directory, k), 'w') as fw:
                        json.dump(v, fw, indent=4)
                del response_data['data']['dsl']
                del response_data['data']['runtime_conf']
                response_data['directory'] = download_directory
                response_data['retmsg'] = 'download successfully, please check {} directory'.format(download_directory)
                response = response_data
        elif func == 'job_log':
            detect_utils.check_config(config=config_data, required_arguments=['job_id', 'output_path'])
            job_id = config_data['job_id']
            tar_file_name = 'job_{}_log.tar.gz'.format(job_id)
            extract_dir = os.path.join(config_data['output_path'], 'job_{}_log'.format(job_id))
            with closing(requests.get("/".join([server_url, func.replace('_', '/')]), json=config_data,
                                      stream=True)) as response:
                if response.status_code == 200:
                    download_from_request(http_response=response, tar_file_name=tar_file_name, extract_dir=extract_dir)
                    response = {'retcode': 0,
                                'directory': extract_dir,
                                'retmsg': 'download successfully, please check {} directory'.format(extract_dir)}
                else:
                    response = response.json()
    elif func in TASK_OPERATE_FUNC:
        response = requests.post("/".join([server_url, "job", "task", func.rstrip('_task')]), json=config_data)
    elif func in TRACKING_FUNC:
        detect_utils.check_config(config=config_data,
                                  required_arguments=['job_id', 'component_name', 'role', 'party_id'])
        if func == 'component_output_data':
            detect_utils.check_config(config=config_data, required_arguments=['output_path'])
            tar_file_name = 'job_{}_{}_{}_{}_output_data.tar.gz'.format(config_data['job_id'],
                                                                        config_data['component_name'],
                                                                        config_data['role'],
                                                                        config_data['party_id'])
            extract_dir = os.path.join(config_data['output_path'], tar_file_name.replace('.tar.gz', ''))
            with closing(requests.get("/".join([server_url, "tracking", func.replace('_', '/'), 'download']),
                                      json=config_data,
                                      stream=True)) as response:
                if response.status_code == 200:
                    download_from_request(http_response=response, tar_file_name=tar_file_name, extract_dir=extract_dir)
                    response = {'retcode': 0,
                                'directory': extract_dir,
                                'retmsg': 'download successfully, please check {} directory'.format(extract_dir)}
                else:
                    response = response.json()

        else:
            response = requests.post("/".join([server_url, "tracking", func.replace('_', '/')]), json=config_data)
    elif func in DATA_FUNC:
        response = requests.post("/".join([server_url, "data", func]), json=config_data)
    elif func in TABLE_FUNC:
        detect_utils.check_config(config=config_data, required_arguments=['namespace', 'table_name'])
        response = requests.post("/".join([server_url, "table", func]), json=config_data)
    elif func in MODEL_FUNC:
        if func == "version":
            detect_utils.check_config(config=config_data, required_arguments=['namespace'])
        response = requests.post("/".join([server_url, "model", func]), json=config_data)
    return response.json() if isinstance(response, requests.models.Response) else response