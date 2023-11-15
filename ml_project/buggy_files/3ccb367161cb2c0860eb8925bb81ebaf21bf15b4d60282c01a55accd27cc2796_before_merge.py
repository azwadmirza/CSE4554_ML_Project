def refresh_gitsavvy(view, refresh_sidebar=False, refresh_status_bar=True,
                     interface_reset_cursor=False):
    """
    Called after GitSavvy action was taken that may have effected the
    state of the Git repo.
    """
    if view is None:
        return

    if view.settings().get("git_savvy.interface") is not None:
        view.run_command("gs_interface_refresh", {"nuke_cursors": interface_reset_cursor})

    if view.settings().get("git_savvy.log_graph_view", False):
        view.run_command("gs_log_graph_refresh")

    if refresh_status_bar:
        view.run_command("gs_update_status_bar")

    if view.window() and refresh_sidebar:
        view.window().run_command("refresh_folder_list")