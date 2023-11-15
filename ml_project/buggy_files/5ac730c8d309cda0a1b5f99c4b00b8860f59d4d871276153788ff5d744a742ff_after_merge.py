def main():
    argument_spec = dict(
        name=dict(type='str', required=True, aliases=['volume_name']),
    )

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        min_docker_version='1.8.0',
        min_docker_api_version='1.21',
    )

    try:
        volume = get_existing_volume(client, client.module.params['name'])

        client.module.exit_json(
            changed=False,
            exists=(True if volume else False),
            volume=volume,
        )
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())
    except RequestException as e:
        client.fail('An unexpected requests error occurred when docker-py tried to talk to the docker daemon: {0}'.format(e), exception=traceback.format_exc())