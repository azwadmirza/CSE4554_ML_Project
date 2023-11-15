def get_project_path(window: 'Any') -> 'Optional[str]':
    """
    Returns the first project folder or the parent folder of the active view
    """
    if len(window.folders()):
        folder_paths = window.folders()
        return folder_paths[0]
    else:
        view = window.active_view()
        if view:
            filename = view.file_name()
            if filename and os.path.exists(filename):  # https://github.com/tomv564/LSP/issues/644
                project_path = os.path.dirname(filename)
                debug("Couldn't determine project directory since no folders are open!",
                      "Using", project_path, "as a fallback.")
                return project_path
            else:
                debug("Couldn't determine project directory since no folders are open",
                      "and the current file isn't saved on the disk.")
                return None
        else:
            debug("No view is active in current window")
            return None  # https://github.com/tomv564/LSP/issues/219