def run_command(jboss_config, command, fail_on_error=True):
    '''
    Execute a command against jboss instance through the CLI interface.

    jboss_config
           Configuration dictionary with properties specified above.
    command
           Command to execute against jboss instance
    fail_on_error (default=True)
           Is true, raise CommandExecutionError exception if execution fails.
           If false, 'success' property of the returned dictionary is set to False

    CLI Example:

    .. code-block:: bash

        salt '*' jboss7_cli.run_command '{"cli_path": "integration.modules.sysmod.SysModuleTest.test_valid_docs", "controller": "10.11.12.13:9999", "cli_user": "jbossadm", "cli_password": "jbossadm"}' my_command
    '''
    cli_command_result = _call_cli(jboss_config, command)

    if cli_command_result['retcode'] == 0:
        cli_command_result['success'] = True
    else:
        if fail_on_error:
            raise CommandExecutionError('''Command execution failed, return code={retcode}, stdout='{stdout}', stderr='{stderr}' '''.format(**cli_command_result))
        else:
            cli_command_result['success'] = False

    return cli_command_result