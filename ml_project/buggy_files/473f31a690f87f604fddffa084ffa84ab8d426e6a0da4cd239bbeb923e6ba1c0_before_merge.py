def main():
    argument_spec = dict(
        auto_remove=dict(type='bool', default=False),
        blkio_weight=dict(type='int'),
        capabilities=dict(type='list', elements='str'),
        cap_drop=dict(type='list', elements='str'),
        cleanup=dict(type='bool', default=False),
        command=dict(type='raw'),
        comparisons=dict(type='dict'),
        cpu_period=dict(type='int'),
        cpu_quota=dict(type='int'),
        cpuset_cpus=dict(type='str'),
        cpuset_mems=dict(type='str'),
        cpu_shares=dict(type='int'),
        detach=dict(type='bool', default=True),
        devices=dict(type='list', elements='str'),
        device_read_bps=dict(type='list', elements='dict', options=dict(
            path=dict(required=True, type='str'),
            rate=dict(required=True, type='str'),
        )),
        device_write_bps=dict(type='list', elements='dict', options=dict(
            path=dict(required=True, type='str'),
            rate=dict(required=True, type='str'),
        )),
        device_read_iops=dict(type='list', elements='dict', options=dict(
            path=dict(required=True, type='str'),
            rate=dict(required=True, type='int'),
        )),
        device_write_iops=dict(type='list', elements='dict', options=dict(
            path=dict(required=True, type='str'),
            rate=dict(required=True, type='int'),
        )),
        dns_servers=dict(type='list', elements='str'),
        dns_opts=dict(type='list', elements='str'),
        dns_search_domains=dict(type='list', elements='str'),
        domainname=dict(type='str'),
        entrypoint=dict(type='list', elements='str'),
        env=dict(type='dict'),
        env_file=dict(type='path'),
        etc_hosts=dict(type='dict'),
        exposed_ports=dict(type='list', elements='str', aliases=['exposed', 'expose']),
        force_kill=dict(type='bool', default=False, aliases=['forcekill']),
        groups=dict(type='list', elements='str'),
        healthcheck=dict(type='dict', options=dict(
            test=dict(type='raw'),
            interval=dict(type='str'),
            timeout=dict(type='str'),
            start_period=dict(type='str'),
            retries=dict(type='int'),
        )),
        hostname=dict(type='str'),
        ignore_image=dict(type='bool', default=False),
        image=dict(type='str'),
        init=dict(type='bool', default=False),
        interactive=dict(type='bool', default=False),
        ipc_mode=dict(type='str'),
        keep_volumes=dict(type='bool', default=True),
        kernel_memory=dict(type='str'),
        kill_signal=dict(type='str'),
        labels=dict(type='dict'),
        links=dict(type='list', elements='str'),
        log_driver=dict(type='str'),
        log_options=dict(type='dict', aliases=['log_opt']),
        mac_address=dict(type='str'),
        memory=dict(type='str', default='0'),
        memory_reservation=dict(type='str'),
        memory_swap=dict(type='str'),
        memory_swappiness=dict(type='int'),
        name=dict(type='str', required=True),
        network_mode=dict(type='str'),
        networks=dict(type='list', elements='dict', options=dict(
            name=dict(type='str', required=True),
            ipv4_address=dict(type='str'),
            ipv6_address=dict(type='str'),
            aliases=dict(type='list', elements='str'),
            links=dict(type='list', elements='str'),
        )),
        networks_cli_compatible=dict(type='bool'),
        oom_killer=dict(type='bool'),
        oom_score_adj=dict(type='int'),
        output_logs=dict(type='bool', default=False),
        paused=dict(type='bool', default=False),
        pid_mode=dict(type='str'),
        pids_limit=dict(type='int'),
        privileged=dict(type='bool', default=False),
        published_ports=dict(type='list', elements='str', aliases=['ports']),
        pull=dict(type='bool', default=False),
        purge_networks=dict(type='bool', default=False),
        read_only=dict(type='bool', default=False),
        recreate=dict(type='bool', default=False),
        restart=dict(type='bool', default=False),
        restart_policy=dict(type='str', choices=['no', 'on-failure', 'always', 'unless-stopped']),
        restart_retries=dict(type='int'),
        runtime=dict(type='str'),
        security_opts=dict(type='list', elements='str'),
        shm_size=dict(type='str'),
        state=dict(type='str', default='started', choices=['absent', 'present', 'started', 'stopped']),
        stop_signal=dict(type='str'),
        stop_timeout=dict(type='int'),
        sysctls=dict(type='dict'),
        tmpfs=dict(type='list', elements='str'),
        trust_image_content=dict(type='bool', default=False),
        tty=dict(type='bool', default=False),
        ulimits=dict(type='list', elements='str'),
        user=dict(type='str'),
        userns_mode=dict(type='str'),
        uts=dict(type='str'),
        volume_driver=dict(type='str'),
        volumes=dict(type='list', elements='str'),
        volumes_from=dict(type='list', elements='str'),
        working_dir=dict(type='str'),
    )

    required_if = [
        ('state', 'present', ['image'])
    ]

    client = AnsibleDockerClientContainer(
        argument_spec=argument_spec,
        required_if=required_if,
        supports_check_mode=True,
        min_docker_api_version='1.20',
    )
    if client.module.params['networks_cli_compatible'] is None and client.module.params['networks']:
        client.module.deprecate(
            'Please note that docker_container handles networks slightly different than docker CLI. '
            'If you specify networks, the default network will still be attached as the first network. '
            '(You can specify purge_networks to remove all networks not explicitly listed.) '
            'This behavior will change in Ansible 2.12. You can change the behavior now by setting '
            'the new `networks_cli_compatible` option to `yes`, and remove this warning by setting '
            'it to `no`',
            version='2.12'
        )

    try:
        cm = ContainerManager(client)
        client.module.exit_json(**sanitize_result(cm.results))
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())