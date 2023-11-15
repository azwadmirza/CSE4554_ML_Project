    def handle_response(self, response: 'Optional[List[Dict]]', pos) -> None:
        window = self.view.window()

        if response is None:
            response = []

        references_count = len(response)
        # return if there are no references
        if references_count < 1:
            window.run_command("hide_panel", {"panel": "output.references"})
            window.status_message("No references found")
            return

        word_region = self.view.word(pos)
        word = self.view.substr(word_region)

        base_dir = get_project_path(window)
        formatted_references = self._get_formatted_references(response, base_dir)

        if settings.show_references_in_quick_panel:
            flags = sublime.KEEP_OPEN_ON_FOCUS_LOST
            if settings.quick_panel_monospace_font:
                flags |= sublime.MONOSPACE_FONT
            window.show_quick_panel(
                self.reflist,
                lambda index: self.on_ref_choice(base_dir, index),
                flags,
                self.get_current_ref(base_dir, word_region.begin()),
                lambda index: self.on_ref_highlight(base_dir, index)
            )
        else:
            panel = ensure_references_panel(window)
            if not panel:
                return
            panel.settings().set("result_base_dir", base_dir)

            panel.set_read_only(False)
            panel.run_command("lsp_clear_panel")
            window.run_command("show_panel", {"panel": "output.references"})
            panel.run_command('append', {
                'characters': "{} references for '{}'\n\n{}".format(references_count, word, formatted_references),
                'force': True,
                'scroll_to_end': False
            })

            # highlight all word occurrences
            regions = panel.find_all(r"\b{}\b".format(word))
            panel.add_regions('ReferenceHighlight', regions, 'comment', flags=sublime.DRAW_OUTLINED)
            panel.set_read_only(True)