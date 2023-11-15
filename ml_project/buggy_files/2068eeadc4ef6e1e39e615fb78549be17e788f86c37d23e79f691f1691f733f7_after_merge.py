def main():
    argument_spec = openstack_full_argument_spec(
        display_name=dict(required=True, aliases=['name']),
        display_description=dict(default=None, aliases=['description']),
        volume=dict(required=True),
        force=dict(required=False, default=False, type='bool'),
        state=dict(default='present', choices=['absent', 'present']),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec,
                           supports_check_mode=True,
                           **module_kwargs)

    sdk, cloud = openstack_cloud_from_module(module)

    state = module.params['state']

    try:
        if cloud.volume_exists(module.params['volume']):
            if module.check_mode:
                module.exit_json(changed=_system_state_change(module, cloud))
            if state == 'present':
                _present_volume_snapshot(module, cloud)
            if state == 'absent':
                _absent_volume_snapshot(module, cloud)
        else:
            module.fail_json(
                msg="No volume with name or id '{0}' was found.".format(
                    module.params['volume']))
    except (sdk.exceptions.OpenStackCloudException, sdk.exceptions.ResourceTimeout) as e:
        module.fail_json(msg=e.message)