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
        builder_cache=dict(type='bool', default=False),
    )

    client = AnsibleDockerClient(
        argument_spec=argument_spec,
        # supports_check_mode=True,
        min_docker_api_version='1.25',
        min_docker_version='2.1.0',
    )

    # Version checks
    cache_min_version = '3.3.0'
    if client.module.params['builder_cache'] and client.docker_py_version < LooseVersion(cache_min_version):
        msg = "Error: Docker SDK for Python's version is %s. Minimum version required for builds option is %s. Use `pip install --upgrade docker` to upgrade."
        client.fail(msg % (docker_version, cache_min_version))

    try:
        result = dict()

        if client.module.params['containers']:
            filters = clean_dict_booleans_for_docker_api(client.module.params.get('containers_filters'))
            res = client.prune_containers(filters=filters)
            result['containers'] = res.get('ContainersDeleted') or []
            result['containers_space_reclaimed'] = res['SpaceReclaimed']

        if client.module.params['images']:
            filters = clean_dict_booleans_for_docker_api(client.module.params.get('images_filters'))
            res = client.prune_images(filters=filters)
            result['images'] = res.get('ImagesDeleted') or []
            result['images_space_reclaimed'] = res['SpaceReclaimed']

        if client.module.params['networks']:
            filters = clean_dict_booleans_for_docker_api(client.module.params.get('networks_filters'))
            res = client.prune_networks(filters=filters)
            result['networks'] = res.get('NetworksDeleted') or []

        if client.module.params['volumes']:
            filters = clean_dict_booleans_for_docker_api(client.module.params.get('volumes_filters'))
            res = client.prune_volumes(filters=filters)
            result['volumes'] = res.get('VolumesDeleted') or []
            result['volumes_space_reclaimed'] = res['SpaceReclaimed']

        if client.module.params['builder_cache']:
            res = client.prune_builds()
            result['builder_cache_space_reclaimed'] = res['SpaceReclaimed']

        client.module.exit_json(**result)
    except DockerException as e:
        client.fail('An unexpected docker error occurred: {0}'.format(e), exception=traceback.format_exc())
    except RequestException as e:
        client.fail('An unexpected requests error occurred when docker-py tried to talk to the docker daemon: {0}'.format(e), exception=traceback.format_exc())