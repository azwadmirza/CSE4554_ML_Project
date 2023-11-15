def main():
    argument_spec = dict(
        advertise_addr=dict(type='str'),
        state=dict(type='str', default='present', choices=['present', 'join', 'absent', 'remove', 'inspect']),
        force=dict(type='bool', default=False),
        listen_addr=dict(type='str', default='0.0.0.0:2377'),
        remote_addrs=dict(type='list', elements='str'),
        join_token=dict(type='str'),
        snapshot_interval=dict(type='int'),
        task_history_retention_limit=dict(type='int'),
        keep_old_snapshots=dict(type='int'),
        log_entries_for_slow_followers=dict(type='int'),
        heartbeat_tick=dict(type='int'),
        election_tick=dict(type='int'),
        dispatcher_heartbeat_period=dict(type='int'),
        node_cert_expiry=dict(type='int'),
        name=dict(type='str'),
        labels=dict(type='dict'),
        signing_ca_cert=dict(type='str'),
        signing_ca_key=dict(type='str'),
        ca_force_rotate=dict(type='int'),
        autolock_managers=dict(type='bool'),
        node_id=dict(type='str'),
        rotate_worker_token=dict(type='bool', default=False),
        rotate_manager_token=dict(type='bool', default=False),
        default_addr_pool=dict(type='list', elements='str'),
        subnet_size=dict(type='int'),
    )

    required_if = [
        ('state', 'join', ['advertise_addr', 'remote_addrs', 'join_token']),
        ('state', 'remove', ['node_id'])
    ]

    option_minimal_versions = dict(
        labels=dict(docker_py_version='2.6.0', docker_api_version='1.32'),
        signing_ca_cert=dict(docker_py_version='2.6.0', docker_api_version='1.30'),
        signing_ca_key=dict(docker_py_version='2.6.0', docker_api_version='1.30'),
        ca_force_rotate=dict(docker_py_version='2.6.0', docker_api_version='1.30'),
        autolock_managers=dict(docker_py_version='2.6.0'),
        log_driver=dict(docker_py_version='2.6.0'),
        remove_operation=dict(
            docker_py_version='2.4.0',
            detect_usage=_detect_remove_operation,
            usage_msg='remove swarm nodes'
        ),
        default_addr_pool=dict(docker_py_version='4.0.0', docker_api_version='1.39'),
        subnet_size=dict(docker_py_version='4.0.0', docker_api_version='1.39'),
    )

    client = AnsibleDockerSwarmClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=required_if,
        min_docker_version='1.10.0',
        min_docker_api_version='1.25',
        option_minimal_versions=option_minimal_versions,
    )

    try:
        results = dict(
            changed=False,
            result='',
            actions=[]
        )

        SwarmManager(client, results)()
        client.module.exit_json(**results)
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())