    def __init__(self, builder: Builder, template_dir: str = None) -> None:
        if template_dir:
            warnings.warn('template_dir argument for AutosummaryRenderer is deprecated.',
                          RemovedInSphinx50Warning)

        system_templates_path = [os.path.join(package_dir, 'ext', 'autosummary', 'templates')]
        loader = SphinxTemplateLoader(builder.srcdir,
                                      builder.config.templates_path,
                                      system_templates_path)

        self.env = SandboxedEnvironment(loader=loader)
        self.env.filters['escape'] = rst.escape
        self.env.filters['e'] = rst.escape
        self.env.filters['underline'] = _underline

        if builder:
            if builder.app.translator:
                self.env.add_extension("jinja2.ext.i18n")
                self.env.install_gettext_translations(builder.app.translator)  # type: ignore