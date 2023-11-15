def create_folder(name, location='\\'):
    r'''
    Create a folder in which to create tasks.

    Args:

        name (str):
            The name of the folder. This will be displayed in the task
            scheduler.

        location (str):
            A string value representing the location in which to create the
            folder. Default is ``\`` which is the root for the task scheduler
            (``C:\Windows\System32\tasks``).

    Returns:
        bool: ``True`` if successful, otherwise ``False``

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' task.create_folder <folder_name>
    '''
    # Check for existing folder
    if name in list_folders(location):
        # Connect to an existing task definition
        return '{0} already exists'.format(name)

    # Create the task service object
    pythoncom.CoInitialize()
    task_service = win32com.client.Dispatch("Schedule.Service")
    task_service.Connect()

    # Get the folder to list folders from
    task_folder = task_service.GetFolder(location)
    task_folder.CreateFolder(name)

    # Verify creation
    if name in list_folders(location):
        return True
    else:
        return False