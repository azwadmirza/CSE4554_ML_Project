def get_project_path(window: 'Any') -> 'Optional[str]':
    """
    Returns the first project folder
    """
    if len(window.folders()):
        folder_paths = window.folders()
        return folder_paths[0]
    return None