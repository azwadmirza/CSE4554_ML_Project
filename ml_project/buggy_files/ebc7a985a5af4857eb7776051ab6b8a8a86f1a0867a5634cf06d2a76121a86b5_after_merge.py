def run(name, location='\\'):
    r'''
    Run a scheduled task manually.

    Args:

        name (str):
            The name of the task to run.

        location (str):
            A string value representing the location of the task. Default is
            ``\`` which is the root for the task scheduler
            (``C:\Windows\System32\tasks``).

    Returns:
        bool: ``True`` if successful, otherwise ``False``

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
    except pythoncom.com_error:
        return False