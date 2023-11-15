def status(name, location='\\'):
    r'''
    Determine the status of a task. Is it Running, Queued, Ready, etc.

    :param str name: The name of the task for which to return the status

    :param str location: A string value representing the location of the task.
        Default is '\\' which is the root for the task scheduler
        (C:\Windows\System32\tasks).

    :return: The current status of the task. Will be one of the following:

    - Unknown
    - Disabled
    - Queued
    - Ready
    - Running

    :rtype: string

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' task.list_status <task_name>
    '''
    # Check for existing folder
    if name not in list_tasks(location):
        return '{0} not found in {1}'.format(name, location)

    # connect to the task scheduler
    pythoncom.CoInitialize()
    task_service = win32com.client.Dispatch("Schedule.Service")
    task_service.Connect()

    # get the folder where the task is defined
    task_folder = task_service.GetFolder(location)
    task = task_folder.GetTask(name)

    return states[task.State]