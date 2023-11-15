    def start_task(job_id, component_name, task_id, role, party_id, task_config):
        schedule_logger.info(
            'job {} {} {} {} task subprocess is ready'.format(job_id, component_name, role, party_id, task_config))
        task_process_start_status = False
        try:
            task_dir = os.path.join(job_utils.get_job_directory(job_id=job_id), role, party_id, component_name)
            os.makedirs(task_dir, exist_ok=True)
            task_config_path = os.path.join(task_dir, 'task_config.json')
            with open(task_config_path, 'w') as fw:
                json.dump(task_config, fw)
            process_cmd = [
                'python3', sys.modules[TaskExecutor.__module__].__file__,
                '-j', job_id,
                '-n', component_name,
                '-t', task_id,
                '-r', role,
                '-p', party_id,
                '-c', task_config_path,
                '--job_server', '{}:{}'.format(task_config['job_server']['ip'], task_config['job_server']['http_port']),
            ]
            task_log_dir = os.path.join(job_utils.get_job_log_directory(job_id=job_id), role, party_id, component_name)
            schedule_logger.info(
                'job {} {} {} {} task subprocess start'.format(job_id, component_name, role, party_id, task_config))
            p = job_utils.run_subprocess(config_dir=task_dir, process_cmd=process_cmd, log_dir=task_log_dir)
            if p:
                task_process_start_status = True
        except Exception as e:
            schedule_logger.exception(e)
        finally:
            schedule_logger.info(
                'job {} component {} on {} {} start task subprocess {}'.format(job_id, component_name, role, party_id,
                                                                               'success' if task_process_start_status else 'failed'))