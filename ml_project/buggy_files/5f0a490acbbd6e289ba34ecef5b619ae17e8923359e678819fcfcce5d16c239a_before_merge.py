def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
    )

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        min_docker_api_version='1.21',
    )

    try:
        network = client.get_network(client.module.params['name'])

        client.module.exit_json(
            changed=False,
            exists=(True if network else False),
            network=network,
        )
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())