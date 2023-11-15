def _save_task_definition(name,
                          task_folder,
                          task_definition,
                          user_name,
                          password,
                          logon_type):
    '''
    Internal function to save the task definition.

    :param str name: The name of the task.

    :param str task_folder: The object representing the folder in which to save
    the task

    :param str task_definition: The object representing the task to be saved

    :param str user_name: The user_account under which to run the task

    :param str password: The password that corresponds to the user account

    :param int logon_type: The logon type for the task.

    :return: True if successful, False if not
    :rtype: bool
    '''
    try:
        task_folder.RegisterTaskDefinition(name,
                                           task_definition,
                                           TASK_CREATE_OR_UPDATE,
                                           user_name,
                                           password,
                                           logon_type)

        return True

    except pythoncom.com_error as error:
        hr, msg, exc, arg = error.args  # pylint: disable=W0633
        fc = {-2147024773: 'The filename, directory name, or volume label '
                           'syntax is incorrect',
              -2147024894: 'The system cannot find the file specified',
              -2147216615: 'Required element or attribute missing',
              -2147216616: 'Value incorrectly formatted or out of range',
              -2147352571: 'Access denied'}
        try:
            failure_code = fc[exc[5]]
        except KeyError:
            failure_code = 'Unknown Failure: {0}'.format(error)

        log.debug('Failed to modify task: {0}'.format(failure_code))

        return 'Failed to modify task: {0}'.format(failure_code)