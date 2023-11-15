def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(required=True),
            validate_certs=dict(required=False, default=True, type='bool', aliases=['verify_ssl']),
            login_user=dict(required=False, no_log=True),
            login_password=dict(required=False, no_log=True),
            login_token=dict(required=False, no_log=True),
            group=dict(required=False),
            name=dict(required=True),
            path=dict(required=False),
            description=dict(required=False),
            issues_enabled=dict(default=True, type='bool'),
            merge_requests_enabled=dict(default=True, type='bool'),
            wiki_enabled=dict(default=True, type='bool'),
            snippets_enabled=dict(default=True, type='bool'),
            public=dict(default=False, type='bool'),
            visibility_level=dict(default="0", choices=["0", "10", "20"]),
            import_url=dict(required=False),
            state=dict(default="present", choices=["present", 'absent']),
        ),
        supports_check_mode=True
    )

    if not HAS_GITLAB_PACKAGE:
        module.fail_json(msg="Missing required gitlab module (check docs or install with: pip install pyapi-gitlab")

    server_url = module.params['server_url']
    verify_ssl = module.params['validate_certs']
    login_user = module.params['login_user']
    login_password = module.params['login_password']
    login_token = module.params['login_token']
    group_name = module.params['group']
    project_name = module.params['name']
    project_path = module.params['path']
    description = module.params['description']
    issues_enabled = module.params['issues_enabled']
    merge_requests_enabled = module.params['merge_requests_enabled']
    wiki_enabled = module.params['wiki_enabled']
    snippets_enabled = module.params['snippets_enabled']
    public = module.params['public']
    visibility_level = module.params['visibility_level']
    import_url = module.params['import_url']
    state = module.params['state']

    # We need both login_user and login_password or login_token, otherwise we fail.
    if login_user is not None and login_password is not None:
        use_credentials = True
    elif login_token is not None:
        use_credentials = False
    else:
        module.fail_json(msg="No login credentials are given. Use login_user with login_password, or login_token")

    # Set project_path to project_name if it is empty.
    if project_path is None:
        project_path = project_name.replace(" ", "_")

    # Gitlab API makes no difference between upper and lower cases, so we lower them.
    project_name = project_name.lower()
    project_path = project_path.lower()
    if group_name is not None:
        group_name = group_name.lower()

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

    # Check if user is authorized or not before proceeding to any operations
    # if not, exit from here
    auth_msg = git.currentuser().get('message', None)
    if auth_msg is not None and auth_msg == '401 Unauthorized':
        module.fail_json(msg='User unauthorized',
                         details="User is not allowed to access Gitlab server "
                                 "using login_token. Please check login_token")

    # Validate if project exists and take action based on "state"
    project = GitLabProject(module, git)
    project_exists = project.existsProject(group_name, project_name)

    # Creating the project dict
    arguments = {"name": project_name,
                 "path": project_path,
                 "description": description,
                 "issues_enabled": project.to_bool(issues_enabled),
                 "merge_requests_enabled": project.to_bool(merge_requests_enabled),
                 "wiki_enabled": project.to_bool(wiki_enabled),
                 "snippets_enabled": project.to_bool(snippets_enabled),
                 "public": project.to_bool(public),
                 "visibility_level": int(visibility_level)}

    if project_exists and state == "absent":
        project.deleteProject(group_name, project_name)
        module.exit_json(changed=True, result="Successfully deleted project %s" % project_name)
    else:
        if state == "absent":
            module.exit_json(changed=False, result="Project deleted or does not exists")
        else:
            if project.createOrUpdateProject(project_exists, group_name, import_url, arguments):
                module.exit_json(changed=True, result="Successfully created or updated the project %s" % project_name)
            else:
                module.exit_json(changed=False)