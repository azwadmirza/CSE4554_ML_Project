        def on_help(event):
            HTMLDialog(
                panel,
                "Workspace viewer help",
                rst_to_html_fragment(WORKSPACE_VIEWER_HELP),
            ).Show()