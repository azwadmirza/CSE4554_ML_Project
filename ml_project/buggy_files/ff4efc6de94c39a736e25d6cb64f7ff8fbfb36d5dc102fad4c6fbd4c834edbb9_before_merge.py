    def finish_job(job_id, job_runtime_conf):
        job_parameters = job_runtime_conf['job_parameters']
        job_initiator = job_runtime_conf['initiator']
        model_id_base64 = base64_encode(job_parameters['model_id'])
        model_version_base64 = base64_encode(job_parameters['model_version'])
        for role, partys in job_runtime_conf['role'].items():
            for party_id in partys:
                # save pipeline
                federated_api(job_id=job_id,
                              method='POST',
                              endpoint='/{}/job/{}/{}/{}/{}/{}/save/pipeline'.format(
                                  API_VERSION,
                                  job_id,
                                  role,
                                  party_id,
                                  model_id_base64,
                                  model_version_base64
                              ),
                              src_party_id=job_initiator['party_id'],
                              dest_party_id=party_id,
                              json_body={},
                              work_mode=job_parameters['work_mode'])
                # clean
                federated_api(job_id=job_id,
                              method='POST',
                              endpoint='/{}/job/{}/{}/{}/clean'.format(
                                  API_VERSION,
                                  job_id,
                                  role,
                                  party_id),
                              src_party_id=job_initiator['party_id'],
                              dest_party_id=party_id,
                              json_body={},
                              work_mode=job_parameters['work_mode'])