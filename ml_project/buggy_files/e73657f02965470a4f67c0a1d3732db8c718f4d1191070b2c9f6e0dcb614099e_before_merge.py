def main():
    argument_spec = dict(
        volume_name=dict(type='str', required=True, aliases=['name']),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        driver=dict(type='str', default='local'),
        driver_options=dict(type='dict', default={}),
        labels=dict(type='dict'),
        force=dict(type='bool', removed_in_version='2.12'),
        recreate=dict(type='str', default='never', choices=['always', 'never', 'options-changed']),
        debug=dict(type='bool', default=False)
    )

    option_minimal_versions = dict(
        labels=dict(docker_py_version='1.10.0', docker_api_version='1.23'),
    )

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        min_docker_version='1.10.0',
        min_docker_api_version='1.21',
        # "The docker server >= 1.9.0"
        option_minimal_versions=option_minimal_versions,
    )

    try:
        cm = DockerVolumeManager(client)
        client.module.exit_json(**cm.results)
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())