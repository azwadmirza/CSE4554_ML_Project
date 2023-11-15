def list_folders(location='\\'):
    r'''
    List all folders located in a specific location in the task scheduler.

    :param str location: A string value representing the folder from which you
        want to list tasks. Default is '\\' which is the root for the task
        scheduler (C:\Windows\System32\tasks).

    :return: Returns a list of folders.
    :rtype: list

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' task.list_folders
    '''
    # Create the task service object
    pythoncom.CoInitialize()
    task_service = win32com.client.Dispatch("Schedule.Service")
    task_service.Connect()

    # Get the folder to list folders from
    task_folder = task_service.GetFolder(location)
    folders = task_folder.GetFolders(0)

    ret = []
    for folder in folders:
        ret.append(folder.Name)

    return ret