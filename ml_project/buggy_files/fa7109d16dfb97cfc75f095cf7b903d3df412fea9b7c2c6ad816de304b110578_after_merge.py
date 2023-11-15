    def handle_response(self, response: 'Optional[List[ReferenceDict]]', pos: int) -> None:
        window = self.view.window()

        if response is None:
            response = []

        references_count = len(response)
        # return if there are no references
        if references_count < 1:
            window.run_command("hide_panel", {"panel": "output.references"})
            window.status_message("No references found")
            return

        references_by_file = self._group_references_by_file(response)

        if settings.show_references_in_quick_panel:
            self.show_quick_panel(references_by_file)
        else:
            self.show_references_panel(references_by_file)