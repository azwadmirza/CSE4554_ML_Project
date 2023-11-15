def main():
    module = AnsibleModule(
        argument_spec = dict(
            state = dict(default='present', choices=['present', 'absent'], type='str'),
            name = dict(required=True, aliases=[ "src", "source" ], type='str'),
            login_user = dict(default='guest', type='str'),
            login_password = dict(default='guest', type='str', no_log=True),
            login_host = dict(default='localhost', type='str'),
            login_port = dict(default='15672', type='str'),
            vhost = dict(default='/', type='str'),
            destination = dict(required=True, aliases=[ "dst", "dest"], type='str'),
            destination_type = dict(required=True, aliases=[ "type", "dest_type"], choices=[ "queue", "exchange" ],type='str'),
            routing_key = dict(default='#', type='str'),
            arguments = dict(default=dict(), type='dict')
        ),
        supports_check_mode = True
    )

    if module.params['destination_type'] == "queue":
        dest_type="q"
    else:
        dest_type="e"

    if module.params['routing_key'] == "":
        props = "~"
    else:
        props = urllib.quote(module.params['routing_key'],'')

    url = "http://%s:%s/api/bindings/%s/e/%s/%s/%s/%s" % (
        module.params['login_host'],
        module.params['login_port'],
        urllib.quote(module.params['vhost'],''),
        urllib.quote(module.params['name'],''),
        dest_type,
        urllib.quote(module.params['destination'],''),
        props
    )

    # Check if exchange already exists
    r = requests.get( url, auth=(module.params['login_user'],module.params['login_password']))

    if r.status_code==200:
        binding_exists = True
        response = r.json()
    elif r.status_code==404:
        binding_exists = False
        response = r.text
    else:
        module.fail_json(
            msg = "Invalid response from RESTAPI when trying to check if exchange exists",
            details = r.text
        )

    if module.params['state']=='present':
        change_required = not binding_exists
    else:
        change_required = binding_exists

    # Exit if check_mode
    if module.check_mode:
        module.exit_json(
            changed= change_required,
            name = module.params['name'],
            details = response,
            arguments = module.params['arguments']
        )

    # Do changes
    if change_required:
        if module.params['state'] == 'present':
            url = "http://%s:%s/api/bindings/%s/e/%s/%s/%s" % (
                module.params['login_host'],
                module.params['login_port'],
                urllib.quote(module.params['vhost'],''),
                urllib.quote(module.params['name'],''),
                dest_type,
                urllib.quote(module.params['destination'],'')
            )

            r = requests.post(
                url,
                auth = (module.params['login_user'],module.params['login_password']),
                headers = { "content-type": "application/json"},
                data = json.dumps({
                    "routing_key": module.params['routing_key'],
                    "arguments": module.params['arguments']
                    })
            )
        elif module.params['state'] == 'absent':
            r = requests.delete( url, auth = (module.params['login_user'],module.params['login_password']))

        if r.status_code == 204 or r.status_code == 201:
            module.exit_json(
                changed = True,
                name = module.params['name'],
                destination = module.params['destination']
            )
        else:
            module.fail_json(
                msg = "Error creating exchange",
                status = r.status_code,
                details = r.text
            )

    else:
        module.exit_json(
            changed = False,
            name = module.params['name']
        )