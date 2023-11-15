    def _reload_modules(self, modules):
        """Reload modules in namespace. Queries sys.modules."""
        for module in modules:
            self.current_import_config = module["config"]
            if isinstance(module["module"], ModuleType):
                module_name = module["module"].__name__
                if sys.modules.get(module_name):
                    _LOGGER.debug("Reloading module %s", module_name)
                    importlib.reload(sys.modules[module_name])