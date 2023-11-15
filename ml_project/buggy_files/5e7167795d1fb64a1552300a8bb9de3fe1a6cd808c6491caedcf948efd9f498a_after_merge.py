    def stop_job(job_id):
        schedule_logger.info('get stop job {} command'.format(job_id))
        jobs = job_utils.query_job(job_id=job_id, is_initiator=1)
        if jobs:
            initiator_job = jobs[0]
            job_info = {'f_job_id': job_id, 'f_status': JobStatus.FAILED}
            roles = json_loads(initiator_job.f_roles)
            job_work_mode = initiator_job.f_work_mode
            initiator_party_id = initiator_job.f_party_id

            # set status first
            TaskScheduler.sync_job_status(job_id=job_id, roles=roles, initiator_party_id=initiator_party_id,
                                          work_mode=job_work_mode,
                                          job_info=job_info)
            for role, partys in roles.items():
                for party_id in partys:
                    response = federated_api(job_id=job_id,
                                             method='POST',
                                             endpoint='/{}/schedule/{}/{}/{}/kill'.format(
                                                 API_VERSION,
                                                 job_id,
                                                 role,
                                                 party_id),
                                             src_party_id=initiator_party_id,
                                             dest_party_id=party_id,
                                             json_body={'job_initiator': {'party_id': initiator_job.f_party_id,
                                                                          'role': initiator_job.f_role}},
                                             work_mode=job_work_mode)
                    if response['retcode'] == 0:
                        schedule_logger.info(
                            'send {} {} kill job {} command successfully'.format(role, party_id, job_id))
                    else:
                        schedule_logger.info(
                            'send {} {} kill job {} command failed: {}'.format(role, party_id, job_id, response['retmsg']))
        else:
            schedule_logger.info('send stop job {} command failed'.format(job_id))
            raise Exception('can not found job: {}'.format(job_id))