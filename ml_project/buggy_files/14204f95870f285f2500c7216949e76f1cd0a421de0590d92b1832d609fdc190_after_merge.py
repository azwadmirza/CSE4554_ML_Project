    def sync_task_status(job_id, component_name, task_id, role, party_id, initiator_party_id, task_info):
        for dest_party_id in {party_id, initiator_party_id}:
            if party_id != initiator_party_id and dest_party_id == initiator_party_id:
                # do not pass the process id to the initiator
                task_info['f_run_ip'] = ''
            federated_api(job_id=job_id,
                          method='POST',
                          endpoint='/{}/schedule/{}/{}/{}/{}/{}/status'.format(
                              API_VERSION,
                              job_id,
                              component_name,
                              task_id,
                              role,
                              party_id),
                          src_party_id=party_id,
                          dest_party_id=dest_party_id,
                          json_body=task_info,
                          work_mode=RuntimeConfig.WORK_MODE)