    def __init__(self, confdir: str, templates_paths: List[str],
                 system_templates_paths: List[str]) -> None:
        self.loaders = []
        self.sysloaders = []

        for templates_path in templates_paths:
            loader = SphinxFileSystemLoader(path.join(confdir, templates_path))
            self.loaders.append(loader)

        for templates_path in system_templates_paths:
            loader = SphinxFileSystemLoader(templates_path)
            self.loaders.append(loader)
            self.sysloaders.append(loader)