def list_folders(location='\\'):
    r'''
    List all folders located in a specific location in the task scheduler.

    Args:

        location (str):
            A string value representing the folder from which you want to list
            tasks. Default is ``\`` which is the root for the task scheduler
            (``C:\Windows\System32\tasks``).

    Returns:
        list: Returns a list of folders.

    CLI Example:

    .. code-block:: bash

        # List all folders in the default location
        salt 'minion-id' task.list_folders

        # List all folders in the Microsoft directory
        salt 'minion-id' task.list_folders Microsoft
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