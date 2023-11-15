def main():

    argument_spec = dict(
        registry_url=dict(type='str', default=DEFAULT_DOCKER_REGISTRY, aliases=['registry', 'url']),
        username=dict(type='str'),
        password=dict(type='str', no_log=True),
        email=dict(type='str'),
        reauthorize=dict(type='bool', default=False, aliases=['reauth']),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        config_path=dict(type='path', default='~/.docker/config.json', aliases=['dockercfg_path']),
    )

    required_if = [
        ('state', 'present', ['username', 'password']),
    ]

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=required_if,
        min_docker_api_version='1.20',
    )

    try:
        results = dict(
            changed=False,
            actions=[],
            login_result={}
        )

        LoginManager(client, results)
        if 'actions' in results:
            del results['actions']
        client.module.exit_json(**results)
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())
    except RequestException as e:
        client.fail('An unexpected requests error occurred when docker-py tried to talk to the docker daemon: {0}'.format(e), exception=traceback.format_exc())