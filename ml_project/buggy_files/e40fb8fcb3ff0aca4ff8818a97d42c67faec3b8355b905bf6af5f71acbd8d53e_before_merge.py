def main():
    module = AnsibleModule(
        argument_spec=dict(
            organization=dict(required=True),
            repo=dict(required=True),
            issue=dict(required=True),
            action=dict(required=False, choices=['get_status']),
        ),
        supports_check_mode=True,
    )

    if not HAS_GITHUB_PACKAGE:
        module.fail_json(msg=missing_required_lib('github3.py >= 1.0.0a4'),
                         exception=GITHUB_IMP_ERR)

    organization = module.params['organization']
    repo = module.params['repo']
    issue = module.params['issue']
    action = module.params['action']

    result = dict()

    gh_obj = github3.issue(organization, repo, issue)
    if gh_obj is None:
        module.fail_json(msg="Failed to get details about issue specified. "
                             "Please check organization, repo and issue "
                             "details and try again.")

    if action == 'get_status' or action is None:
        if module.check_mode:
            result.update(changed=True)
        else:
            result.update(changed=True, issue_status=gh_obj.state)

    module.exit_json(**result)