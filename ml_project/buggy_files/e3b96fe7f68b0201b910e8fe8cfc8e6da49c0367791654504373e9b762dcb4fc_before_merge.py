def list_actions(name, location='\\'):
    r'''
    List all actions that pertain to a task in the specified location.

    :param str name: The name of the task for which list actions.

    :param str location: A string value representing the location of the task
        from which to list actions. Default is '\\' which is the root for the
        task scheduler (C:\Windows\System32\tasks).

    :return: Returns a list of actions.
    :rtype: list

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' task.list_actions <task_name>
    '''
    # Create the task service object
    pythoncom.CoInitialize()
    task_service = win32com.client.Dispatch("Schedule.Service")
    task_service.Connect()

    # Get the folder to list folders from
    task_folder = task_service.GetFolder(location)
    task_definition = task_folder.GetTask(name).Definition
    actions = task_definition.Actions

    ret = []
    for action in actions:
        ret.append(action.Id)

    return ret