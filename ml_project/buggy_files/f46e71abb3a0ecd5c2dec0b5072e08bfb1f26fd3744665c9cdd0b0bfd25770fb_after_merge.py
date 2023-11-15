def main():
    argument_spec = dict(
        iam_type=dict(required=True, choices=['user', 'group', 'role']),
        state=dict(default='present', choices=['present', 'absent']),
        iam_name=dict(default=None, required=False),
        policy_name=dict(required=True),
        policy_document=dict(default=None, required=False),
        policy_json=dict(type='json', default=None, required=False),
        skip_duplicates=dict(type='bool', default=None, required=False)
    )
    mutually_exclusive = [['policy_document', 'policy_json']]

    module = AnsibleAWSModule(argument_spec=argument_spec, mutually_exclusive=mutually_exclusive, supports_check_mode=True)

    skip_duplicates = module.params.get('skip_duplicates')

    if (skip_duplicates is None):
        module.deprecate('The skip_duplicates behaviour has caused confusion and'
                         ' will be disabled by default in Ansible 2.14',
                         version='2.14')
        skip_duplicates = True

    if module.params.get('policy_document'):
        module.deprecate('The policy_document option has been deprecated and'
                         ' will be removed in Ansible 2.14',
                         version='2.14')

    args = dict(
        client=module.client('iam'),
        name=module.params.get('iam_name'),
        policy_name=module.params.get('policy_name'),
        policy_document=module.params.get('policy_document'),
        policy_json=module.params.get('policy_json'),
        skip_duplicates=skip_duplicates,
        state=module.params.get('state'),
        check_mode=module.check_mode,
    )
    iam_type = module.params.get('iam_type')

    try:
        if iam_type == 'user':
            policy = UserPolicy(**args)
        elif iam_type == 'role':
            policy = RolePolicy(**args)
        elif iam_type == 'group':
            policy = GroupPolicy(**args)

        module.exit_json(**(policy.run()))
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e)
    except PolicyError as e:
        module.fail_json(msg=str(e))