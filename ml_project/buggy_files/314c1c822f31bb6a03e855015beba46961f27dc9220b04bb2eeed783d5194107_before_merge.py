def main():
    argument_spec = dict(
        project_src=dict(type='path'),
        project_name=dict(type='str',),
        files=dict(type='list', elements='path'),
        state=dict(type='str', default='present', choices=['absent', 'present']),
        definition=dict(type='dict'),
        hostname_check=dict(type='bool', default=False),
        recreate=dict(type='str', default='smart', choices=['always', 'never', 'smart']),
        build=dict(type='bool', default=False),
        remove_images=dict(type='str', choices=['all', 'local']),
        remove_volumes=dict(type='bool', default=False),
        remove_orphans=dict(type='bool', default=False),
        stopped=dict(type='bool', default=False),
        restarted=dict(type='bool', default=False),
        scale=dict(type='dict'),
        services=dict(type='list', elements='str'),
        dependencies=dict(type='bool', default=True),
        pull=dict(type='bool', default=False),
        nocache=dict(type='bool', default=False),
        debug=dict(type='bool', default=False),
        timeout=dict(type='int', default=DEFAULT_TIMEOUT)
    )

    mutually_exclusive = [
        ('definition', 'project_src'),
        ('definition', 'files')
    ]

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        mutually_exclusive=mutually_exclusive,
        supports_check_mode=True,
        min_docker_api_version='1.20',
    )
    if client.module._name == 'docker_service':
        client.module.deprecate("The 'docker_service' module has been renamed to 'docker_compose'.", version='2.12')

    try:
        result = ContainerManager(client).exec_module()
        client.module.exit_json(**result)
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())