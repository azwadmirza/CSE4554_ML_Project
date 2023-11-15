def update_diagnostics_panel(window: sublime.Window):
    assert window, "missing window!"

    if not window.is_valid():
        debug('ignoring update to closed window')
        return

    base_dir = windows.lookup(window).get_project_path()

    diagnostics_by_file = get_window_diagnostics(window)
    if diagnostics_by_file is not None:

        active_panel = window.active_panel()
        is_active_panel = (active_panel == "output.diagnostics")

        if diagnostics_by_file:
            panel = ensure_diagnostics_panel(window)
            assert panel, "must have a panel now!"
            panel.settings().set("result_base_dir", base_dir)

            auto_open_panel = False
            to_render = []
            for file_path, source_diagnostics in diagnostics_by_file.items():
                try:
                    relative_file_path = os.path.relpath(file_path, base_dir) if base_dir else file_path
                except ValueError:
                    relative_file_path = file_path
                if source_diagnostics:
                    formatted = format_diagnostics(relative_file_path, source_diagnostics)
                    if formatted:
                        to_render.append(formatted)
                        if not auto_open_panel:
                            auto_open_panel = has_relevant_diagnostics(source_diagnostics)

            panel.set_read_only(False)
            panel.run_command("lsp_update_panel", {"characters": "\n".join(to_render)})
            panel.set_read_only(True)

            if settings.auto_show_diagnostics_panel and not active_panel:
                if auto_open_panel:
                    window.run_command("show_panel",
                                       {"panel": "output.diagnostics"})

        else:
            panel = window.find_output_panel("diagnostics")
            if panel:
                panel.run_command("lsp_clear_panel")
                if is_active_panel:
                    window.run_command("hide_panel",
                                       {"panel": "output.diagnostics"})