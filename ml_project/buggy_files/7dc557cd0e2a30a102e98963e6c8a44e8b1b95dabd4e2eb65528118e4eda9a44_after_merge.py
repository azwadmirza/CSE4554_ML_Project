def update_resources(module, p):
    '''update_resources attempts to fetch any of the resources given
    by name using their unique field (identity)
    '''
    params = p.copy()
    identity_map = {
        'user': 'username',
        'team': 'name',
        'target_team': 'name',
        'inventory': 'name',
        'job_template': 'name',
        'credential': 'name',
        'organization': 'name',
        'project': 'name',
    }
    for k, v in identity_map.items():
        try:
            if params[k]:
                key = 'team' if k == 'target_team' else k
                result = tower_cli.get_resource(key).get(**{v: params[k]})
                params[k] = result['id']
        except (exc.NotFound) as excinfo:
            module.fail_json(msg='Failed to update role, {0} not found: {1}'.format(k, excinfo), changed=False)
    return params