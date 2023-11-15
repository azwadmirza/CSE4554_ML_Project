    def copy_theme_static_files(self, context: Dict) -> None:
        if self.theme:
            for entry in self.theme.get_theme_dirs()[::-1]:
                copy_asset(path.join(entry, 'static'),
                           path.join(self.outdir, '_static'),
                           excluded=DOTFILES, context=context, renderer=self.templates)