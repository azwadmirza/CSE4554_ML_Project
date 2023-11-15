    def run_async(self, settings=None, cached=False):
        if settings is None:
            file_view = self.window.active_view()
            syntax_file = file_view.settings().get("syntax")
            settings = {
                "git_savvy.file_path": self.file_path,
                "git_savvy.repo_path": self.repo_path
            }
        else:
            syntax_file = settings["syntax"]
            del settings["syntax"]

        view_key = "{0}+{1}".format(cached, settings["git_savvy.file_path"])

        if view_key in inline_diff_views and inline_diff_views[view_key] in sublime.active_window().views():
            diff_view = inline_diff_views[view_key]
        else:
            diff_view = util.view.get_scratch_view(self, "inline_diff", read_only=True)
            title = INLINE_DIFF_CACHED_TITLE if cached else INLINE_DIFF_TITLE
            diff_view.set_name(title + os.path.basename(settings["git_savvy.file_path"]))

            diff_view.set_syntax_file(syntax_file)
            file_ext = util.file.get_file_extension(os.path.basename(settings["git_savvy.file_path"]))
            self.augment_color_scheme(diff_view, file_ext)

            diff_view.settings().set("git_savvy.inline_diff.cached", cached)
            for k, v in settings.items():
                diff_view.settings().set(k, v)

            inline_diff_views[view_key] = diff_view

        file_binary = util.file.get_file_contents_binary(self.repo_path, self.file_path)
        try:
            file_binary.decode()
        except UnicodeDecodeError as unicode_err:
            try:
                file_binary.decode("latin-1")
                diff_view.settings().set("git_savvy.inline_diff.encoding", "latin-1")
            except UnicodeDecodeError as unicode_err:
                savvy_settings = sublime.load_settings("GitSavvy.sublime-settings")
                fallback_encoding = savvy_settings.get("fallback_encoding")
                diff_view.settings().set("git_savvy.inline_diff.encoding", fallback_encoding)

        self.window.focus_view(diff_view)

        diff_view.run_command("gs_inline_diff_refresh")
        diff_view.run_command("gs_handle_vintageous")