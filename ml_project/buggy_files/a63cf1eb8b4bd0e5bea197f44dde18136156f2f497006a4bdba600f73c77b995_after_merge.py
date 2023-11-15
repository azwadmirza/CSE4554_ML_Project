    def copy_theme_static_files(self, context: Dict) -> None:
        def onerror(filename: str, error: Exception) -> None:
            logger.warning(__('Failed to copy a file in html_static_file: %s: %r'),
                           filename, error)

        if self.theme:
            for entry in self.theme.get_theme_dirs()[::-1]:
                copy_asset(path.join(entry, 'static'),
                           path.join(self.outdir, '_static'),
                           excluded=DOTFILES, context=context,
                           renderer=self.templates, onerror=onerror)