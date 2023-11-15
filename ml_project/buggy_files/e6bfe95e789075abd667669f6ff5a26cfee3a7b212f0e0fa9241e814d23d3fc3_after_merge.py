def run_operation(jboss_config, operation, fail_on_error=True, retries=1):
    '''
    Execute an operation against jboss instance through the CLI interface.

    jboss_config
           Configuration dictionary with properties specified above.
    operation
           An operation to execute against jboss instance

    fail_on_error (default=True)
           Is true, raise CommandExecutionError exception if execution fails.
           If false, 'success' property of the returned dictionary is set to False
    retries:
           Number of retries in case of "JBAS012144: Could not connect to remote" error.

    CLI Example:

    .. code-block:: bash

        salt '*' jboss7_cli.run_operation '{"cli_path": "integration.modules.sysmod.SysModuleTest.test_valid_docs", "controller": "10.11.12.13:9999", "cli_user": "jbossadm", "cli_password": "jbossadm"}' my_operation
    '''
    cli_command_result = _call_cli(jboss_config, operation, retries)

    if cli_command_result['retcode'] == 0:
        if _is_cli_output(cli_command_result['stdout']):
            cli_result = _parse(cli_command_result['stdout'])
            cli_result['success'] = cli_result['outcome'] == 'success'
        else:
            raise CommandExecutionError('Operation has returned unparseable output: {0}'.format(cli_command_result['stdout']))
    else:
        if _is_cli_output(cli_command_result['stdout']):
            cli_result = _parse(cli_command_result['stdout'])
            cli_result['success'] = False

            match = re.search(r'^(JBAS\d+):', cli_result['failure-description'])
            # if match is None then check for wildfly error code
            if match is None:
                match = re.search(r'^(WFLYCTL\d+):', cli_result['failure-description'])

            if match is not None:
                cli_result['err_code'] = match.group(1)
            else:
                # Could not find err_code
                log.error("Jboss 7 operation failed! Error Code could not be found!")
                cli_result['err_code'] = '-1'

            cli_result['stdout'] = cli_command_result['stdout']
        else:
            if fail_on_error:
                raise CommandExecutionError('''Command execution failed, return code={retcode}, stdout='{stdout}', stderr='{stderr}' '''.format(**cli_command_result))
            else:
                cli_result = {
                    'success': False,
                    'stdout': cli_command_result['stdout'],
                    'stderr': cli_command_result['stderr'],
                    'retcode': cli_command_result['retcode']
                }
    return cli_result