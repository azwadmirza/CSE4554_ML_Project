    def _reload_modules(self, modules):
        for module in modules:
            self.current_import_config = module["config"]
            importlib.reload(module["module"])