    def run_task():
        task = Task()
        task.f_create_time = current_timestamp()
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument('-j', '--job_id', required=True, type=str, help="job id")
            parser.add_argument('-n', '--component_name', required=True, type=str,
                                help="component name")
            parser.add_argument('-t', '--task_id', required=True, type=str, help="task id")
            parser.add_argument('-r', '--role', required=True, type=str, help="role")
            parser.add_argument('-p', '--party_id', required=True, type=str, help="party id")
            parser.add_argument('-c', '--config', required=True, type=str, help="task config")
            parser.add_argument('--job_server', help="job server", type=str)
            args = parser.parse_args()
            schedule_logger.info('enter task process')
            schedule_logger.info(args)
            # init function args
            if args.job_server:
                RuntimeConfig.init_config(HTTP_PORT=args.job_server.split(':')[1])
            job_id = args.job_id
            component_name = args.component_name
            task_id = args.task_id
            role = args.role
            party_id = int(args.party_id)
            task_config = file_utils.load_json_conf(args.config)
            job_parameters = task_config['job_parameters']
            job_initiator = task_config['job_initiator']
            job_args = task_config['job_args']
            task_input_dsl = task_config['input']
            task_output_dsl = task_config['output']
            parameters = task_config['parameters']
            module_name = task_config['module_name']
        except Exception as e:
            schedule_logger.exception(e)
            task.f_status = TaskStatus.FAILED
            return
        try:
            # init environment, process is shared globally
            RuntimeConfig.init_config(WORK_MODE=job_parameters['work_mode'])
            storage.init_storage(job_id=task_id, work_mode=RuntimeConfig.WORK_MODE)
            federation.init(job_id=task_id, runtime_conf=parameters)
            job_log_dir = os.path.join(job_utils.get_job_log_directory(job_id=job_id), role, str(party_id))
            task_log_dir = os.path.join(job_log_dir, component_name)
            log_utils.LoggerFactory.set_directory(directory=task_log_dir, parent_log_dir=job_log_dir,
                                                  append_to_parent_log=True, force=True)

            task.f_job_id = job_id
            task.f_component_name = component_name
            task.f_task_id = task_id
            task.f_role = role
            task.f_party_id = party_id
            task.f_operator = 'python_operator'
            tracker = Tracking(job_id=job_id, role=role, party_id=party_id, component_name=component_name,
                               task_id=task_id,
                               model_id=job_parameters['model_id'],
                               model_version=job_parameters['model_version'],
                               module_name=module_name)
            task.f_start_time = current_timestamp()
            task.f_run_ip = get_lan_ip()
            task.f_run_pid = os.getpid()
            run_class_paths = parameters.get('CodePath').split('/')
            run_class_package = '.'.join(run_class_paths[:-2]) + '.' + run_class_paths[-2].rstrip('.py')
            run_class_name = run_class_paths[-1]
            task_run_args = TaskExecutor.get_task_run_args(job_id=job_id, role=role, party_id=party_id,
                                                           job_parameters=job_parameters, job_args=job_args,
                                                           input_dsl=task_input_dsl)
            run_object = getattr(importlib.import_module(run_class_package), run_class_name)()
            run_object.set_tracker(tracker=tracker)
            run_object.set_taskid(taskid=task_id)
            task.f_status = TaskStatus.RUNNING
            TaskExecutor.sync_task_status(job_id=job_id, component_name=component_name, task_id=task_id, role=role,
                                          party_id=party_id, initiator_party_id=job_initiator.get('party_id', None),
                                          task_info=task.to_json())

            schedule_logger.info('run {} {} {} {} {} task'.format(job_id, component_name, task_id, role, party_id))
            schedule_logger.info(parameters)
            schedule_logger.info(task_input_dsl)
            run_object.run(parameters, task_run_args)
            if task_output_dsl:
                if task_output_dsl.get('data', []):
                    output_data = run_object.save_data()
                    tracker.save_output_data_table(output_data, task_output_dsl.get('data')[0])
                if task_output_dsl.get('model', []):
                    output_model = run_object.export_model()
                    # There is only one model output at the current dsl version.
                    tracker.save_output_model(output_model, task_output_dsl['model'][0])
            task.f_status = TaskStatus.SUCCESS
        except Exception as e:
            schedule_logger.exception(e)
            task.f_status = TaskStatus.FAILED
        finally:
            try:
                task.f_end_time = current_timestamp()
                task.f_elapsed = task.f_end_time - task.f_start_time
                task.f_update_time = current_timestamp()
                TaskExecutor.sync_task_status(job_id=job_id, component_name=component_name, task_id=task_id, role=role,
                                              party_id=party_id,
                                              initiator_party_id=job_initiator.get('party_id', None),
                                              task_info=task.to_json())
            except Exception as e:
                schedule_logger.exception(e)
        schedule_logger.info(
            'finish {} {} {} {} {} {} task'.format(job_id, component_name, task_id, role, party_id, task.f_status))
        print('finish {} {} {} {} {} {} task'.format(job_id, component_name, task_id, role, party_id, task.f_status))