    def __init__(self, builder: Builder, template_dir: str) -> None:
        loader = None  # type: BaseLoader
        template_dirs = [os.path.join(package_dir, 'ext', 'autosummary', 'templates')]
        if builder is None:
            if template_dir:
                template_dirs.insert(0, template_dir)
            loader = FileSystemLoader(template_dirs)
        else:
            # allow the user to override the templates
            loader = BuiltinTemplateLoader()
            loader.init(builder, dirs=template_dirs)

        self.env = SandboxedEnvironment(loader=loader)
        self.env.filters['escape'] = rst.escape
        self.env.filters['e'] = rst.escape
        self.env.filters['underline'] = _underline

        if builder:
            if builder.app.translator:
                self.env.add_extension("jinja2.ext.i18n")
                self.env.install_gettext_translations(builder.app.translator)  # type: ignore