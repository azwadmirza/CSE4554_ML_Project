def run(name, location='\\'):
    r'''
    Run a scheduled task manually.

    :param str name: The name of the task to run.

    :param str location: A string value representing the location of the task.
        Default is '\\' which is the root for the task scheduler
        (C:\Windows\System32\tasks).

    :return: True if successful, False if unsuccessful
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' task.list_run <task_name>
    '''
    # Check for existing folder
    if name not in list_tasks(location):
        return '{0} not found in {1}'.format(name, location)

    # connect to the task scheduler
    pythoncom.CoInitialize()
    task_service = win32com.client.Dispatch("Schedule.Service")
    task_service.Connect()

    # get the folder to delete the folder from
    task_folder = task_service.GetFolder(location)
    task = task_folder.GetTask(name)

    try:
        task.Run('')
        return True
    except pythoncom.com_error as error:
        return False