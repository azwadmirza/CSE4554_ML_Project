def main():
    argument_spec = dict(
        name=dict(type='str', required=True),
    )

    client = AnsibleDockerSwarmClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        min_docker_version='2.0.0',
        min_docker_api_version='1.24',
    )

    client.fail_task_if_not_swarm_manager()

    try:
        service = get_service_info(client)

        client.module.exit_json(
            changed=False,
            service=service,
            exists=bool(service)
        )
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())