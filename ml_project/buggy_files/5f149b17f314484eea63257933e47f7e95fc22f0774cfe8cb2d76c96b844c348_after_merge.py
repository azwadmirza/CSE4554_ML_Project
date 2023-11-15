def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
        image=dict(type='str'),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        mounts=dict(type='list', elements='dict', options=dict(
            source=dict(type='str', required=True),
            target=dict(type='str', required=True),
            type=dict(
                type='str',
                default='bind',
                choices=['bind', 'volume', 'tmpfs'],
            ),
            readonly=dict(type='bool'),
            labels=dict(type='dict'),
            propagation=dict(
                type='str',
                choices=[
                    'shared',
                    'slave',
                    'private',
                    'rshared',
                    'rslave',
                    'rprivate'
                ]
            ),
            no_copy=dict(type='bool'),
            driver_config=dict(type='dict', options=dict(
                name=dict(type='str'),
                options=dict(type='dict')
            )),
            tmpfs_size=dict(type='str'),
            tmpfs_mode=dict(type='int')
        )),
        configs=dict(type='list', elements='dict', options=dict(
            config_id=dict(type='str'),
            config_name=dict(type='str', required=True),
            filename=dict(type='str'),
            uid=dict(type='str'),
            gid=dict(type='str'),
            mode=dict(type='int'),
        )),
        secrets=dict(type='list', elements='dict', options=dict(
            secret_id=dict(type='str'),
            secret_name=dict(type='str', required=True),
            filename=dict(type='str'),
            uid=dict(type='str'),
            gid=dict(type='str'),
            mode=dict(type='int'),
        )),
        networks=dict(type='list', elements='str'),
        command=dict(type='raw'),
        args=dict(type='list', elements='str'),
        env=dict(type='raw'),
        env_files=dict(type='list', elements='path'),
        force_update=dict(type='bool', default=False),
        groups=dict(type='list', elements='str'),
        logging=dict(type='dict', options=dict(
            driver=dict(type='str'),
            options=dict(type='dict'),
        )),
        log_driver=dict(type='str', removed_in_version='2.12'),
        log_driver_options=dict(type='dict', removed_in_version='2.12'),
        publish=dict(type='list', elements='dict', options=dict(
            published_port=dict(type='int', required=True),
            target_port=dict(type='int', required=True),
            protocol=dict(type='str', default='tcp', choices=['tcp', 'udp']),
            mode=dict(type='str', choices=['ingress', 'host']),
        )),
        placement=dict(type='dict', options=dict(
            constraints=dict(type='list'),
            preferences=dict(type='list'),
        )),
        constraints=dict(type='list', removed_in_version='2.12'),
        tty=dict(type='bool'),
        dns=dict(type='list'),
        dns_search=dict(type='list'),
        dns_options=dict(type='list'),
        healthcheck=dict(type='dict', options=dict(
            test=dict(type='raw'),
            interval=dict(type='str'),
            timeout=dict(type='str'),
            start_period=dict(type='str'),
            retries=dict(type='int'),
        )),
        hostname=dict(type='str'),
        hosts=dict(type='dict'),
        labels=dict(type='dict'),
        container_labels=dict(type='dict'),
        mode=dict(
            type='str',
            default='replicated',
            choices=['replicated', 'global']
        ),
        replicas=dict(type='int', default=-1),
        endpoint_mode=dict(type='str', choices=['vip', 'dnsrr']),
        stop_grace_period=dict(type='str'),
        stop_signal=dict(type='str'),
        limits=dict(type='dict', options=dict(
            cpus=dict(type='float'),
            memory=dict(type='str'),
        )),
        limit_cpu=dict(type='float', removed_in_version='2.12'),
        limit_memory=dict(type='str', removed_in_version='2.12'),
        read_only=dict(type='bool'),
        reservations=dict(type='dict', options=dict(
            cpus=dict(type='float'),
            memory=dict(type='str'),
        )),
        reserve_cpu=dict(type='float', removed_in_version='2.12'),
        reserve_memory=dict(type='str', removed_in_version='2.12'),
        resolve_image=dict(type='bool', default=False),
        restart_config=dict(type='dict', options=dict(
            condition=dict(type='str', choices=['none', 'on-failure', 'any']),
            delay=dict(type='str'),
            max_attempts=dict(type='int'),
            window=dict(type='str'),
        )),
        restart_policy=dict(
            type='str',
            choices=['none', 'on-failure', 'any'],
            removed_in_version='2.12'
        ),
        restart_policy_delay=dict(type='raw', removed_in_version='2.12'),
        restart_policy_attempts=dict(type='int', removed_in_version='2.12'),
        restart_policy_window=dict(type='raw', removed_in_version='2.12'),
        rollback_config=dict(type='dict', options=dict(
            parallelism=dict(type='int'),
            delay=dict(type='str'),
            failure_action=dict(
                type='str',
                choices=['continue', 'pause']
            ),
            monitor=dict(type='str'),
            max_failure_ratio=dict(type='float'),
            order=dict(type='str'),
        )),
        update_config=dict(type='dict', options=dict(
            parallelism=dict(type='int'),
            delay=dict(type='str'),
            failure_action=dict(
                type='str',
                choices=['continue', 'pause', 'rollback']
            ),
            monitor=dict(type='str'),
            max_failure_ratio=dict(type='float'),
            order=dict(type='str'),
        )),
        update_delay=dict(type='raw', removed_in_version='2.12'),
        update_parallelism=dict(type='int', removed_in_version='2.12'),
        update_failure_action=dict(
            type='str',
            choices=['continue', 'pause', 'rollback'],
            removed_in_version='2.12'
        ),
        update_monitor=dict(type='raw', removed_in_version='2.12'),
        update_max_failure_ratio=dict(type='float', removed_in_version='2.12'),
        update_order=dict(
            type='str',
            choices=['stop-first', 'start-first'],
            removed_in_version='2.12'
        ),
        user=dict(type='str'),
        working_dir=dict(type='str'),
    )

    option_minimal_versions = dict(
        constraints=dict(docker_py_version='2.4.0'),
        dns=dict(docker_py_version='2.6.0', docker_api_version='1.25'),
        dns_options=dict(docker_py_version='2.6.0', docker_api_version='1.25'),
        dns_search=dict(docker_py_version='2.6.0', docker_api_version='1.25'),
        endpoint_mode=dict(docker_py_version='3.0.0', docker_api_version='1.25'),
        force_update=dict(docker_py_version='2.1.0', docker_api_version='1.25'),
        healthcheck=dict(docker_py_version='2.6.0', docker_api_version='1.25'),
        hostname=dict(docker_py_version='2.2.0', docker_api_version='1.25'),
        hosts=dict(docker_py_version='2.6.0', docker_api_version='1.25'),
        groups=dict(docker_py_version='2.6.0', docker_api_version='1.25'),
        tty=dict(docker_py_version='2.4.0', docker_api_version='1.25'),
        secrets=dict(docker_py_version='2.4.0', docker_api_version='1.25'),
        configs=dict(docker_py_version='2.6.0', docker_api_version='1.30'),
        update_max_failure_ratio=dict(docker_py_version='2.1.0', docker_api_version='1.25'),
        update_monitor=dict(docker_py_version='2.1.0', docker_api_version='1.25'),
        update_order=dict(docker_py_version='2.7.0', docker_api_version='1.29'),
        stop_signal=dict(docker_py_version='2.6.0', docker_api_version='1.28'),
        publish=dict(docker_py_version='3.0.0', docker_api_version='1.25'),
        read_only=dict(docker_py_version='2.6.0', docker_api_version='1.28'),
        resolve_image=dict(docker_api_version='1.30', docker_py_version='3.2.0'),
        rollback_config=dict(docker_py_version='3.5.0', docker_api_version='1.28'),
        # specials
        publish_mode=dict(
            docker_py_version='3.0.0',
            docker_api_version='1.25',
            detect_usage=_detect_publish_mode_usage,
            usage_msg='set publish.mode'
        ),
        healthcheck_start_period=dict(
            docker_py_version='2.4.0',
            docker_api_version='1.25',
            detect_usage=_detect_healthcheck_start_period,
            usage_msg='set healthcheck.start_period'
        ),
        update_config_max_failure_ratio=dict(
            docker_py_version='2.1.0',
            docker_api_version='1.25',
            detect_usage=lambda c: (c.module.params['update_config'] or {}).get(
                'max_failure_ratio'
            ) is not None,
            usage_msg='set update_config.max_failure_ratio'
        ),
        update_config_failure_action=dict(
            docker_py_version='3.5.0',
            docker_api_version='1.28',
            detect_usage=_detect_update_config_failure_action_rollback,
            usage_msg='set update_config.failure_action.rollback'
        ),
        update_config_monitor=dict(
            docker_py_version='2.1.0',
            docker_api_version='1.25',
            detect_usage=lambda c: (c.module.params['update_config'] or {}).get(
                'monitor'
            ) is not None,
            usage_msg='set update_config.monitor'
        ),
        update_config_order=dict(
            docker_py_version='2.7.0',
            docker_api_version='1.29',
            detect_usage=lambda c: (c.module.params['update_config'] or {}).get(
                'order'
            ) is not None,
            usage_msg='set update_config.order'
        ),
        placement_config_preferences=dict(
            docker_py_version='2.4.0',
            docker_api_version='1.27',
            detect_usage=lambda c: (c.module.params['placement'] or {}).get(
                'preferences'
            ) is not None,
            usage_msg='set placement.preferences'
        ),
        placement_config_constraints=dict(
            docker_py_version='2.4.0',
            detect_usage=lambda c: (c.module.params['placement'] or {}).get(
                'constraints'
            ) is not None,
            usage_msg='set placement.constraints'
        ),
        mounts_tmpfs=dict(
            docker_py_version='2.6.0',
            detect_usage=_detect_mount_tmpfs_usage,
            usage_msg='set mounts.tmpfs'
        ),
        rollback_config_order=dict(
            docker_api_version='1.29',
            detect_usage=lambda c: (c.module.params['rollback_config'] or {}).get(
                'order'
            ) is not None,
            usage_msg='set rollback_config.order'
        ),
    )
    required_if = [
        ('state', 'present', ['image'])
    ]

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        required_if=required_if,
        supports_check_mode=True,
        min_docker_version='2.0.2',
        min_docker_api_version='1.24',
        option_minimal_versions=option_minimal_versions,
    )

    try:
        dsm = DockerServiceManager(client)
        msg, changed, rebuilt, changes, facts = dsm.run_safe()

        results = dict(
            msg=msg,
            changed=changed,
            rebuilt=rebuilt,
            changes=changes,
            swarm_service=facts,
        )
        if client.module._diff:
            before, after = dsm.diff_tracker.get_before_after()
            results['diff'] = dict(before=before, after=after)

        client.module.exit_json(**results)
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())
    except RequestException as e:
        client.fail('An unexpected requests error occurred when docker-py tried to talk to the docker daemon: {0}'.format(e), exception=traceback.format_exc())