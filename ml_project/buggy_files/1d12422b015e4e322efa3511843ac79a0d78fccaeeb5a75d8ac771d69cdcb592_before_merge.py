    def sync_job_status(job_id, roles, work_mode, initiator_party_id, job_info):
        for role, partys in roles.items():
            job_info['f_role'] = role
            for party_id in partys:
                job_info['f_party_id'] = party_id
                federated_api(job_id=job_id,
                              method='POST',
                              endpoint='/{}/job/{}/{}/{}/status'.format(
                                  API_VERSION,
                                  job_id,
                                  role,
                                  party_id),
                              src_party_id=initiator_party_id,
                              dest_party_id=party_id,
                              json_body=job_info,
                              work_mode=work_mode)