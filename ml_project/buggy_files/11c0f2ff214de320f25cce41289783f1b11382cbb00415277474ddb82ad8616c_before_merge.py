    def on_ref_highlight(self, base_dir: 'Optional[str]', index: int) -> None:
        window = self.view.window()
        if index != -1:
            window.open_file(self.get_selected_file_path(base_dir, index), sublime.ENCODED_POSITION | sublime.TRANSIENT)