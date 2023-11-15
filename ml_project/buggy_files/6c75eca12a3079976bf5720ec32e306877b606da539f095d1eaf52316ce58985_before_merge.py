def main():
    argument_spec = dict(
        name=dict(type='list', elements='str'),
        self=dict(type='bool', default=False),
    )

    client = AnsibleDockerSwarmClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        min_docker_version='2.4.0',
        min_docker_api_version='1.24',
    )

    client.fail_task_if_not_swarm_manager()

    try:
        nodes = get_node_facts(client)

        client.module.exit_json(
            changed=False,
            nodes=nodes,
        )
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())