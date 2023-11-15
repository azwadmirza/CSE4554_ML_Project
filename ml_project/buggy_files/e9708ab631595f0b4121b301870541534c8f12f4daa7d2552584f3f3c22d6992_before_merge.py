def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            validate_certs=dict(required=False, default=True, type='bool', aliases=['verify_ssl']),
            login_user=dict(required=False, no_log=True),
            login_password=dict(required=False, no_log=True),
            login_token=dict(required=False, no_log=True),
            name=dict(required=True),
            path=dict(required=False),
            state=dict(default="present", choices=["present", "absent"]),
        ),
        supports_check_mode=True
    )

    if not HAS_GITLAB_PACKAGE:
        module.fail_json(msg="Missing requried gitlab module (check docs or install with: pip install pyapi-gitlab")

    server_url = module.params['server_url']
    verify_ssl = module.params['validate_certs']
    login_user = module.params['login_user']
    login_password = module.params['login_password']
    login_token = module.params['login_token']
    group_name = module.params['name']
    group_path = module.params['path']
    state = module.params['state']

    # We need both login_user and login_password or login_token, otherwise we fail.
    if login_user is not None and login_password is not None:
        use_credentials = True
    elif login_token is not None:
        use_credentials = False
    else:
        module.fail_json(msg="No login credentials are given. Use login_user with login_password, or login_token")

    # Set group_path to group_name if it is empty.
    if group_path is None:
        group_path = group_name.replace(" ", "_")

    # Lets make an connection to the Gitlab server_url, with either login_user and login_password
    # or with login_token
    try:
        if use_credentials:
            git = gitlab.Gitlab(host=server_url, verify_ssl=verify_ssl)
            git.login(user=login_user, password=login_password)
        else:
            git = gitlab.Gitlab(server_url, token=login_token, verify_ssl=verify_ssl)
    except Exception:
        e = get_exception()
        module.fail_json(msg="Failed to connect to Gitlab server: %s " % e)

    # Validate if group exists and take action based on "state"
    group = GitLabGroup(module, git)
    group_name = group_name.lower()
    group_exists = group.existsGroup(group_name)

    if group_exists and state == "absent":
        group.deleteGroup(group_name)
        module.exit_json(changed=True, result="Successfully deleted group %s" % group_name)
    else:
        if state == "absent":
            module.exit_json(changed=False, result="Group deleted or does not exists")
        else:
            if group_exists:
                module.exit_json(changed=False)
            else:
                if group.createGroup(group_name, group_path):
                    module.exit_json(changed=True, result="Successfully created or updated the group %s" % group_name)