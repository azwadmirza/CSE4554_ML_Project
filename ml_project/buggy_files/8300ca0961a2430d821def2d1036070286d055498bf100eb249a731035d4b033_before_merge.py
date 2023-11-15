def main():
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type='str', default=os.environ.get('VMWARE_HOST')),
            username=dict(type='str', default=os.environ.get('VMWARE_USER')),
            password=dict(type='str', default=os.environ.get('VMWARE_PASSWORD'), no_log=True),
            state=dict(type='str', default='present',
                       choices=['absent', 'poweredoff', 'poweredon', 'present', 'rebootguest', 'restarted', 'shutdownguest', 'suspended']),
            validate_certs=dict(type='bool', default=True),
            template=dict(type='str', aliases=['template_src']),
            is_template=dict(type='bool', default=False),
            annotation=dict(type='str', aliases=['notes']),
            customvalues=dict(type='list', default=[]),
            name=dict(type='str', required=True),
            name_match=dict(type='str', default='first'),
            uuid=dict(type='str'),
            folder=dict(type='str', default='/vm'),
            guest_id=dict(type='str'),
            disk=dict(type='list', default=[]),
            hardware=dict(type='dict', default={}),
            force=dict(type='bool', default=False),
            datacenter=dict(type='str', default='ha-datacenter'),
            esxi_hostname=dict(type='str'),
            cluster=dict(type='str'),
            wait_for_ip_address=dict(type='bool', default=False),
            snapshot_src=dict(type='str'),
            linked_clone=dict(type='bool', default=False),
            networks=dict(type='list', default=[]),
            resource_pool=dict(type='str'),
            customization=dict(type='dict', default={}, no_log=True),
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ['cluster', 'esxi_hostname'],
        ],
    )

    result = {'failed': False, 'changed': False}

    # FindByInventoryPath() does not require an absolute path
    # so we should leave the input folder path unmodified
    module.params['folder'] = module.params['folder'].rstrip('/')

    pyv = PyVmomiHelper(module)

    # Check if the VM exists before continuing
    vm = pyv.getvm(name=module.params['name'], folder=module.params['folder'], uuid=module.params['uuid'])

    # VM already exists
    if vm:
        if module.params['state'] == 'absent':
            # destroy it
            if module.params['force']:
                # has to be poweredoff first
                pyv.set_powerstate(vm, 'poweredoff', module.params['force'])
            result = pyv.remove_vm(vm)
        elif module.params['state'] == 'present':
            result = pyv.reconfigure_vm()
        elif module.params['state'] in ['poweredon', 'poweredoff', 'restarted', 'suspended', 'shutdownguest', 'rebootguest']:
            # set powerstate
            tmp_result = pyv.set_powerstate(vm, module.params['state'], module.params['force'])
            if tmp_result['changed']:
                result["changed"] = True
            if not tmp_result["failed"]:
                result["failed"] = False
        else:
            # This should not happen
            assert False
    # VM doesn't exist
    else:
        if module.params['state'] in ['poweredon', 'poweredoff', 'present', 'restarted', 'suspended']:
            # Create it ...
            result = pyv.deploy_vm()

    if result['failed']:
        module.fail_json(**result)
    else:
        module.exit_json(**result)