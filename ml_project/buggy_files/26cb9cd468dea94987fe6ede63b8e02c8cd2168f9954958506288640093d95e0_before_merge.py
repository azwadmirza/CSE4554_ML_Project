    def update_job_status(job_id, role, party_id, job_info, create=False):
        job_tracker = Tracking(job_id=job_id, role=role, party_id=party_id)
        job_info['f_run_ip'] = get_lan_ip()
        if create:
            dsl = json_loads(job_info['f_dsl'])
            runtime_conf = json_loads(job_info['f_runtime_conf'])
            train_runtime_conf = json_loads(job_info['f_train_runtime_conf'])
            save_job_conf(job_id=job_id,
                          job_dsl=dsl,
                          job_runtime_conf=runtime_conf)
            roles = json_loads(job_info['f_roles'])
            partner = {}
            show_role = {}
            is_initiator = job_info.get('f_is_initiator', 0)
            for _role, _role_party in roles.items():
                if is_initiator or _role == role:
                    show_role[_role] = show_role.get(_role, [])
                    for _party_id in _role_party:
                        if is_initiator or _party_id == party_id:
                            show_role[_role].append(_party_id)

                if _role != role:
                    partner[_role] = partner.get(_role, [])
                    partner[_role].extend(_role_party)
                else:
                    for _party_id in _role_party:
                        if _party_id != party_id:
                            partner[_role] = partner.get(_role, [])
                            partner[_role].append(_party_id)

            dag = get_job_dsl_parser(dsl=dsl,
                                     runtime_conf=runtime_conf,
                                     train_runtime_conf=train_runtime_conf)
            job_args = dag.get_args_input()
            dataset = {}
            for _role, _role_party_args in job_args.items():
                if is_initiator or _role == role:
                    for _party_index in range(len(_role_party_args)):
                        _party_id = roles[_role][_party_index]
                        if is_initiator or _party_id == party_id:
                            dataset[_role] = dataset.get(_role, {})
                            dataset[_role][_party_id] = dataset[_role].get(_party_id, {})
                            for _data_type, _data_location in _role_party_args[_party_index]['args']['data'].items():
                                dataset[_role][_party_id][_data_type] = '{}.{}'.format(_data_location['namespace'],
                                                                                       _data_location['name'])
            job_tracker.log_job_view({'partner': partner, 'dataset': dataset, 'roles': show_role})
        job_tracker.save_job_info(role=role, party_id=party_id, job_info=job_info, create=create)