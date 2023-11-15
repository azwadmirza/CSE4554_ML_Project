    def copy_html_static_files(self, context: Dict) -> None:
        def onerror(filename: str, error: Exception) -> None:
            logger.warning(__('Failed to copy a file in html_static_file: %s: %r'),
                           filename, error)

        excluded = Matcher(self.config.exclude_patterns + ["**/.*"])
        for entry in self.config.html_static_path:
            copy_asset(path.join(self.confdir, entry),
                       path.join(self.outdir, '_static'),
                       excluded, context=context, renderer=self.templates, onerror=onerror)