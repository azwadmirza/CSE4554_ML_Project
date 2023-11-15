def list_tasks(location='\\'):
    r'''
    List all tasks located in a specific location in the task scheduler.

    :param str location: A string value representing the folder from which you
        want to list tasks. Default is '\\' which is the root for the task
        scheduler (C:\Windows\System32\tasks).

    :return: Returns a list of tasks.
    :rtype: list

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' task.list_tasks
    '''
    # Create the task service object
    pythoncom.CoInitialize()
    task_service = win32com.client.Dispatch("Schedule.Service")
    task_service.Connect()

    # Get the folder to list tasks from
    task_folder = task_service.GetFolder(location)
    tasks = task_folder.GetTasks(0)

    ret = []
    for task in tasks:
        ret.append(task.Name)

    return ret