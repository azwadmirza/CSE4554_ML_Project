def main():
    module = AnsibleModule(
        argument_spec=dict(
            organization=dict(required=True),
            repo=dict(required=True),
            issue=dict(type='int', required=True),
            action=dict(choices=['get_status'], default='get_status'),
        ),
        supports_check_mode=True,
    )

    organization = module.params['organization']
    repo = module.params['repo']
    issue = module.params['issue']
    action = module.params['action']

    result = dict()

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.github.v3+json',
    }

    url = "https://api.github.com/repos/%s/%s/issues/%s" % (organization, repo, issue)

    response, info = fetch_url(module, url, headers=headers)
    if not (200 <= info['status'] < 400):
        if info['status'] == 404:
            module.fail_json(msg="Failed to find issue %s" % issue)
        module.fail_json(msg="Failed to send request to %s: %s" % (url, info['msg']))

    gh_obj = json.loads(response.read())

    if action == 'get_status' or action is None:
        if module.check_mode:
            result.update(changed=True)
        else:
            result.update(changed=True, issue_status=gh_obj['state'])

    module.exit_json(**result)