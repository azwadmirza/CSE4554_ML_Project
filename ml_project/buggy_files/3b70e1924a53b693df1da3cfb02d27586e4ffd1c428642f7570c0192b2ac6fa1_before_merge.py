def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = ServiceNowClient.snow_argument_spec()
    module_args.update(
        table=dict(type='str', required=False, default='incident'),
        state=dict(choices=['present', 'absent'],
                   type='str', required=True),
        number=dict(default=None, required=False, type='str'),
        data=dict(default=None, required=False, type='dict'),
        lookup_field=dict(default='number', required=False, type='str'),
        attachment=dict(default=None, required=False, type='str')
    )
    module_required_together = [
        ['client_id', 'client_secret']
    ]
    module_required_if = [
        ['state', 'absent', ['number']],
    ]

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_together=module_required_together,
        required_if=module_required_if
    )

    # Connect to ServiceNow
    service_now_client = ServiceNowClient(module)
    service_now_client.login()
    conn = service_now_client.conn

    params = module.params
    instance = params['instance']
    table = params['table']
    state = params['state']
    number = params['number']
    data = params['data']
    lookup_field = params['lookup_field']

    result = dict(
        changed=False,
        instance=instance,
        table=table,
        number=number,
        lookup_field=lookup_field
    )

    # check for attachments
    if params['attachment'] is not None:
        attach = params['attachment']
        b_attach = to_bytes(attach, errors='surrogate_or_strict')
        if not os.path.exists(b_attach):
            module.fail_json(msg="Attachment {0} not found".format(attach))
        result['attachment'] = attach
    else:
        attach = None

    # Deal with check mode
    if module.check_mode:

        # if we are in check mode and have no number, we would have created
        # a record.  We can only partially simulate this
        if number is None:
            result['record'] = dict(data)
            result['changed'] = True

        # do we want to check if the record is non-existent?
        elif state == 'absent':
            try:
                record = conn.query(table=table, query={lookup_field: number})
                res = record.get_one()
                result['record'] = dict(Success=True)
                result['changed'] = True
            except pysnow.exceptions.NoResults:
                result['record'] = None
            except Exception as detail:
                module.fail_json(msg="Unknown failure in query record: {0}".format(to_native(detail)), **result)

        # Let's simulate modification
        else:
            try:
                record = conn.query(table=table, query={lookup_field: number})
                res = record.get_one()
                for key, value in data.items():
                    res[key] = value
                    result['changed'] = True
                result['record'] = res
            except pysnow.exceptions.NoResults:
                snow_error = "Record does not exist"
                module.fail_json(msg=snow_error, **result)
            except Exception as detail:
                module.fail_json(msg="Unknown failure in query record: {0}".format(to_native(detail)), **result)
        module.exit_json(**result)

    # now for the real thing: (non-check mode)

    # are we creating a new record?
    if state == 'present' and number is None:
        try:
            record = conn.insert(table=table, payload=dict(data))
        except pysnow.exceptions.UnexpectedResponseFormat as e:
            snow_error = "Failed to create record: {0}, details: {1}".format(e.error_summary, e.error_details)
            module.fail_json(msg=snow_error, **result)
        result['record'] = record
        result['changed'] = True

    # we are deleting a record
    elif state == 'absent':
        try:
            record = conn.query(table=table, query={lookup_field: number})
            res = record.delete()
        except pysnow.exceptions.NoResults:
            res = dict(Success=True)
        except pysnow.exceptions.MultipleResults:
            snow_error = "Multiple record match"
            module.fail_json(msg=snow_error, **result)
        except pysnow.exceptions.UnexpectedResponseFormat as e:
            snow_error = "Failed to delete record: {0}, details: {1}".format(e.error_summary, e.error_details)
            module.fail_json(msg=snow_error, **result)
        except Exception as detail:
            snow_error = "Failed to delete record: {0}".format(to_native(detail))
            module.fail_json(msg=snow_error, **result)
        result['record'] = res
        result['changed'] = True

    # We want to update a record
    else:
        try:
            record = conn.query(table=table, query={lookup_field: number})
            if data is not None:
                res = record.update(dict(data))
                result['record'] = res
                result['changed'] = True
            else:
                res = record.get_one()
                result['record'] = res
            if attach is not None:
                res = record.attach(b_attach)
                result['changed'] = True
                result['attached_file'] = res

        except pysnow.exceptions.MultipleResults:
            snow_error = "Multiple record match"
            module.fail_json(msg=snow_error, **result)
        except pysnow.exceptions.NoResults:
            snow_error = "Record does not exist"
            module.fail_json(msg=snow_error, **result)
        except pysnow.exceptions.UnexpectedResponseFormat as e:
            snow_error = "Failed to update record: {0}, details: {1}".format(e.error_summary, e.error_details)
            module.fail_json(msg=snow_error, **result)
        except Exception as detail:
            snow_error = "Failed to update record: {0}".format(to_native(detail))
            module.fail_json(msg=snow_error, **result)

    module.exit_json(**result)