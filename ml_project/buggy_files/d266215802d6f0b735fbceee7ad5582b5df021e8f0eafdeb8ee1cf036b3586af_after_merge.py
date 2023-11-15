def main():
    argument_spec = dict(
        all=dict(type='bool', default=False),
        credential=dict(type='list', default=[]),
        credential_type=dict(type='list', default=[]),
        inventory=dict(type='list', default=[]),
        inventory_script=dict(type='list', default=[]),
        job_template=dict(type='list', default=[]),
        notification_template=dict(type='list', default=[]),
        organization=dict(type='list', default=[]),
        project=dict(type='list', default=[]),
        team=dict(type='list', default=[]),
        user=dict(type='list', default=[]),
        workflow=dict(type='list', default=[]),
    )

    module = TowerModule(argument_spec=argument_spec, supports_check_mode=False)

    if not HAS_TOWER_CLI:
        module.fail_json(msg='ansible-tower-cli required for this module')

    if not TOWER_CLI_HAS_EXPORT:
        module.fail_json(msg='ansible-tower-cli version does not support export')

    export_all = module.params.get('all')
    assets_to_export = {}
    for asset_type in SEND_ORDER:
        assets_to_export[asset_type] = module.params.get(asset_type)

    result = dict(
        assets=None,
        changed=False,
        message='',
    )

    tower_auth = tower_auth_config(module)
    with settings.runtime_values(**tower_auth):
        try:
            receiver = Receiver()
            result['assets'] = receiver.export_assets(all=export_all, asset_input=assets_to_export)
            module.exit_json(**result)
        except TowerCLIError as e:
            result['message'] = e.message
            module.fail_json(msg='Receive Failed', **result)