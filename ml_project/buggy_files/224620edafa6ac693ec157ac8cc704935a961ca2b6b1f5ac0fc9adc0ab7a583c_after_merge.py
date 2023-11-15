def main():
    argument_spec = dict(
        nodes=dict(type='bool', default=False),
        nodes_filters=dict(type='dict'),
        tasks=dict(type='bool', default=False),
        tasks_filters=dict(type='dict'),
        services=dict(type='bool', default=False),
        services_filters=dict(type='dict'),
        unlock_key=dict(type='bool', default=False),
        verbose_output=dict(type='bool', default=False),
    )
    option_minimal_versions = dict(
        unlock_key=dict(docker_py_version='2.7.0', docker_api_version='1.25'),
    )

    client = AnsibleDockerSwarmClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        min_docker_version='1.10.0',
        min_docker_api_version='1.24',
        option_minimal_versions=option_minimal_versions,
        fail_results=dict(
            can_talk_to_docker=False,
            docker_swarm_active=False,
            docker_swarm_manager=False,
        ),
    )
    client.fail_results['can_talk_to_docker'] = True
    client.fail_results['docker_swarm_active'] = client.check_if_swarm_node()
    client.fail_results['docker_swarm_manager'] = client.check_if_swarm_manager()

    try:
        results = dict(
            changed=False,
        )

        DockerSwarmManager(client, results)
        results.update(client.fail_results)
        client.module.exit_json(**results)
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())
    except RequestException as e:
        client.fail('An unexpected requests error occurred when docker-py tried to talk to the docker daemon: {0}'.format(e), exception=traceback.format_exc())