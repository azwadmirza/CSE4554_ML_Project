    def run_component(job_id, job_runtime_conf, job_parameters, job_initiator, job_args, dag, component):
        parameters = component.get_role_parameters()
        component_name = component.get_name()
        module_name = component.get_module()
        task_id = job_utils.generate_task_id(job_id=job_id, component_name=component_name)
        schedule_logger.info('job {} run component {}'.format(job_id, component_name))
        for role, partys_parameters in parameters.items():
            for party_index in range(len(partys_parameters)):
                party_parameters = partys_parameters[party_index]
                if role in job_args:
                    party_job_args = job_args[role][party_index]['args']
                else:
                    party_job_args = {}
                dest_party_id = party_parameters.get('local', {}).get('party_id')

                federated_api(job_id=job_id,
                              method='POST',
                              endpoint='/{}/schedule/{}/{}/{}/{}/{}/run'.format(
                                  API_VERSION,
                                  job_id,
                                  component_name,
                                  task_id,
                                  role,
                                  dest_party_id),
                              src_party_id=job_initiator['party_id'],
                              dest_party_id=dest_party_id,
                              json_body={'job_parameters': job_parameters,
                                         'job_initiator': job_initiator,
                                         'job_args': party_job_args,
                                         'parameters': party_parameters,
                                         'module_name': module_name,
                                         'input': component.get_input(),
                                         'output': component.get_output(),
                                         'job_server': {'ip': get_lan_ip(), 'http_port': RuntimeConfig.HTTP_PORT}},
                              work_mode=job_parameters['work_mode'])
        component_task_status = TaskScheduler.check_task_status(job_id=job_id, component=component)
        if component_task_status:
            task_success = True
        else:
            task_success = False
        schedule_logger.info(
            'job {} component {} run {}'.format(job_id, component_name, 'success' if task_success else 'failed'))
        # update progress
        TaskScheduler.sync_job_status(job_id=job_id, roles=job_runtime_conf['role'],
                                      work_mode=job_parameters['work_mode'],
                                      initiator_party_id=job_initiator['party_id'],
                                      job_info=job_utils.update_job_progress(job_id=job_id, dag=dag,
                                                                             current_task_id=task_id).to_json())
        if task_success:
            next_components = dag.get_next_components(component_name)
            schedule_logger.info('job {} component {} next components is {}'.format(job_id, component_name,
                                                                                    [next_component.get_name() for
                                                                                     next_component in
                                                                                     next_components]))
            for next_component in next_components:
                try:
                    schedule_logger.info(
                        'job {} check component {} dependencies status'.format(job_id, next_component.get_name()))
                    dependencies_status = TaskScheduler.check_dependencies(job_id=job_id, dag=dag,
                                                                           component=next_component)
                    schedule_logger.info(
                        'job {} component {} dependencies status is {}'.format(job_id, next_component.get_name(),
                                                                               dependencies_status))
                    if dependencies_status:
                        run_status = TaskScheduler.run_component(job_id, job_runtime_conf, job_parameters,
                                                                 job_initiator, job_args, dag,
                                                                 next_component)
                    else:
                        run_status = False
                except Exception as e:
                    schedule_logger.info(e)
                    run_status = False
                if not run_status:
                    return False
            return True
        else:
            return False