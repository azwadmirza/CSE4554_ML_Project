def main():
    argument_spec = dict(
        containers=dict(type='bool', default=False),
        containers_filters=dict(type='dict'),
        images=dict(type='bool', default=False),
        images_filters=dict(type='dict'),
        networks=dict(type='bool', default=False),
        networks_filters=dict(type='dict'),
        volumes=dict(type='bool', default=False),
        volumes_filters=dict(type='dict'),
        disk_usage=dict(type='bool', default=False),
        verbose_output=dict(type='bool', default=False),
    )

    option_minimal_versions = dict(
        network_filters=dict(docker_py_version='2.0.2'),
        disk_usage=dict(docker_py_version='2.2.0'),
    )

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        min_docker_version='1.10.0',
        min_docker_api_version='1.21',
        option_minimal_versions=option_minimal_versions,
        fail_results=dict(
            can_talk_to_docker=False,
        ),
    )
    client.fail_results['can_talk_to_docker'] = True

    try:
        results = dict(
            changed=False,
        )

        DockerHostManager(client, results)
        client.module.exit_json(**results)
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())
    except RequestException as e:
        client.fail('An unexpected requests error occurred when docker-py tried to talk to the docker daemon: {0}'.format(e), exception=traceback.format_exc())