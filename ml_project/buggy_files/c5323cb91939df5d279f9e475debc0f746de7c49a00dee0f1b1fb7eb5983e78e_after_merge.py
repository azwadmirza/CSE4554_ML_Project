def main():
    argument_spec = dict(
        volume_name=dict(type='str', required=True, aliases=['name']),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        driver=dict(type='str', default='local'),
        driver_options=dict(type='dict', default={}),
        labels=dict(type='dict'),
        force=dict(type='bool', default=False),
        debug=dict(type='bool', default=False)
    )

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        min_docker_version='1.10.0',
        # "The docker server >= 1.9.0"
    )

    cm = DockerVolumeManager(client)
    client.module.exit_json(**cm.results)