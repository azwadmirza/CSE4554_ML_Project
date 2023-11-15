    def distribute_job(job, roles, job_initiator):
        for role, partys in roles.items():
            job.f_role = role
            for party_id in partys:
                job.f_party_id = party_id
                if role == job_initiator['role'] and party_id == job_initiator['party_id']:
                    job.f_is_initiator = 1
                else:
                    job.f_is_initiator = 0
                federated_api(job_id=job.f_job_id,
                              method='POST',
                              endpoint='/{}/job/{}/{}/{}/create'.format(
                                  API_VERSION,
                                  job.f_job_id,
                                  role,
                                  party_id),
                              src_party_id=job_initiator['party_id'],
                              dest_party_id=party_id,
                              json_body=job.to_json(),
                              work_mode=job.f_work_mode)