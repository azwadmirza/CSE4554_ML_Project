def main():
    argument_spec = dict(
        hostname=dict(type='str', required=True),
        labels=dict(type='dict'),
        labels_state=dict(type='str', default='merge', choices=['merge', 'replace']),
        labels_to_remove=dict(type='list', elements='str'),
        availability=dict(type='str', choices=['active', 'pause', 'drain']),
        role=dict(type='str', choices=['worker', 'manager']),
    )

    client = AnsibleDockerSwarmClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        min_docker_version='2.4.0',
        min_docker_api_version='1.25',
    )

    try:
        results = dict(
            changed=False,
        )

        SwarmNodeManager(client, results)
        client.module.exit_json(**results)
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())