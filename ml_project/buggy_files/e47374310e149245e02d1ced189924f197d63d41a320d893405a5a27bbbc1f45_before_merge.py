def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        name                 = dict(required=True),
        schedule_expression  = dict(),
        event_pattern        = dict(),
        state                = dict(choices=['present', 'disabled', 'absent'],
                                    default='present'),
        description          = dict(),
        role_arn             = dict(),
        targets              = dict(type='list', default=[]),
    ))
    module = AnsibleModule(argument_spec=argument_spec)

    if not HAS_BOTO3:
        module.fail_json(msg='boto3 required for this module')

    rule_data = dict(
        [(rf, module.params.get(rf)) for rf in CloudWatchEventRuleManager.RULE_FIELDS]
    )
    targets = module.params.get('targets')
    state = module.params.get('state')

    cwe_rule = CloudWatchEventRule(module,
                                   client=get_cloudwatchevents_client(module),
                                   **rule_data)
    cwe_rule_manager = CloudWatchEventRuleManager(cwe_rule, targets)

    if state == 'present':
        cwe_rule_manager.ensure_present()
    elif state == 'disabled':
        cwe_rule_manager.ensure_disabled()
    elif state == 'absent':
        cwe_rule_manager.ensure_absent()
    else:
        module.fail_json(msg="Invalid state '{0}' provided".format(state))

    module.exit_json(**cwe_rule_manager.fetch_aws_state())