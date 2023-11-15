def delete_folder(name, location='\\'):
    r'''
    Delete a folder from the task scheduler.

    Args:

        name (str):
            The name of the folder to delete.

        location (str):
            A string value representing the location of the folder.  Default is
            ``\`` which is the root for the task scheduler
            (``C:\Windows\System32\tasks``).

    Returns:
        bool: ``True`` if successful, otherwise ``False``

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' task.delete_folder <folder_name>
    '''
    # Check for existing folder
    if name not in list_folders(location):
        return '{0} not found in {1}'.format(name, location)

    # connect to the task scheduler
    pythoncom.CoInitialize()
    task_service = win32com.client.Dispatch("Schedule.Service")
    task_service.Connect()

    # get the folder to delete the folder from
    task_folder = task_service.GetFolder(location)

    # Delete the folder
    task_folder.DeleteFolder(name, 0)

    # Verify deletion
    if name not in list_folders(location):
        return True
    else:
        return False