def main():
    argument_spec = dict(
        name=dict(type='list', elements='str'),
    )

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        supports_check_mode=True,
        min_docker_api_version='1.20',
    )
    if client.module._name == 'docker_image_facts':
        client.module.deprecate("The 'docker_image_facts' module has been renamed to 'docker_image_info'", version='2.12')

    try:
        results = dict(
            changed=False,
            images=[]
        )

        ImageManager(client, results)
        client.module.exit_json(**results)
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())
    except RequestException as e:
        client.fail('An unexpected requests error occurred when docker-py tried to talk to the docker daemon: {0}'.format(e), exception=traceback.format_exc())