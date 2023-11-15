def delete_task(name, location='\\'):
    r'''
    Delete a task from the task scheduler.

    :param str name: The name of the task to delete.

    :param str location: A string value representing the location of the task.
        Default is '\\' which is the root for the task scheduler
        (C:\Windows\System32\tasks).

    :return: True if successful, False if unsuccessful
    :rtype: bool

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' task.delete_task <task_name>
    '''
    # Check for existing task
    if name not in list_tasks(location):
        return '{0} not found in {1}'.format(name, location)

    # connect to the task scheduler
    pythoncom.CoInitialize()
    task_service = win32com.client.Dispatch("Schedule.Service")
    task_service.Connect()

    # get the folder to delete the task from
    task_folder = task_service.GetFolder(location)

    task_folder.DeleteTask(name, 0)

    # Verify deletion
    if name not in list_tasks(location):
        return True
    else:
        return False