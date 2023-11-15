def main():
    argument_spec = dict(
        assets=dict(required=False),
        files=dict(required=False, default=[], type='list'),
        prevent=dict(required=False, default=[], type='list'),
        password_management=dict(required=False, default='default', choices=['default', 'random']),
    )

    module = TowerModule(argument_spec=argument_spec, supports_check_mode=False)

    if not HAS_TOWER_CLI:
        module.fail_json(msg='ansible-tower-cli required for this module')

    if not TOWER_CLI_HAS_EXPORT:
        module.fail_json(msg='ansible-tower-cli version does not support export')

    assets = module.params.get('assets')
    prevent = module.params.get('prevent')
    password_management = module.params.get('password_management')
    files = module.params.get('files')

    result = dict(
        changed=False,
        msg='',
        output='',
    )

    if not assets and not files:
        result['msg'] = "Assets or files must be specified"
        module.fail_json(**result)

    path = None
    if assets:
        # We got assets so we need to dump this out to a temp file and append that to files
        handle, path = mkstemp(prefix='', suffix='', dir='')
        with open(path, 'w') as f:
            f.write(assets)
        files.append(path)

    tower_auth = tower_auth_config(module)
    failed = False
    with settings.runtime_values(**tower_auth):
        try:
            sender = Sender(no_color=False)
            old_stdout = sys.stdout
            sys.stdout = captured_stdout = StringIO()
            try:
                sender.send(files, prevent, password_management)
            except TypeError as e:
                # Newer versions of TowerCLI require 4 parameters
                sender.send(files, prevent, [], password_management)

            if sender.error_messages > 0:
                failed = True
                result['msg'] = "Transfer Failed with %d errors" % sender.error_messages
            if sender.changed_messages > 0:
                result['changed'] = True
        except TowerCLIError as e:
            result['msg'] = e
            failed = True
        finally:
            if path is not None:
                os.remove(path)
            result['output'] = captured_stdout.getvalue().split("\n")
            sys.stdout = old_stdout

    # Return stdout so that module returns will work
    if failed:
        module.fail_json(**result)
    else:
        module.exit_json(**result)