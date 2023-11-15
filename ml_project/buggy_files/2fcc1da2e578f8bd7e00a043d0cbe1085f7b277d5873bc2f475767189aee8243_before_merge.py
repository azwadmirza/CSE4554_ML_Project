    def _load_modules(self, modules_type, modules):
        """Install and load modules.

        Args:
            self: instance method
            modules_type (str): Type of module being loaded
            modules (dict): Dictionary containing all modules

        Returns:
            list: modules and their config information

        """
        _LOGGER.debug(_("Loading %s modules..."), modules_type)
        loaded_modules = list()

        if not os.path.isdir(DEFAULT_MODULE_DEPS_PATH):
            os.makedirs(DEFAULT_MODULE_DEPS_PATH)
        sys.path.append(DEFAULT_MODULE_DEPS_PATH)

        # entry point group naming scheme: opsdroid_ + module type plural,
        # eg. "opsdroid_databases"
        epname = "opsdroid_{}s".format(modules_type)
        entry_points = {ep.name: ep for ep in iter_entry_points(group=epname)}
        for epname in entry_points:
            _LOGGER.debug(
                _("Found installed package for %s '%s' support."), modules_type, epname
            )

        for module in modules:
            config = self.setup_module_config(
                modules, module, modules_type, entry_points
            )

            # If the module isn't builtin, or isn't already on the
            # python path, install it
            if not (config["is_builtin"] or config["module"] or config["entrypoint"]):
                # Remove module for reinstall if no-cache set
                self.check_cache(config)

                # Install or update module
                if not self._is_module_installed(config):
                    self._install_module(config)
                else:
                    self._update_module(config)

            # Import module
            self.current_import_config = config
            module = self.import_module(config)

            # Suppress exception if module doesn't contain CONFIG_SCHEMA
            with contextlib.suppress(AttributeError):
                validate_configuration(config, module.CONFIG_SCHEMA)

            # Load intents
            intents = self._load_intents(config)

            if module is not None:
                loaded_modules.append(
                    {"module": module, "config": config, "intents": intents}
                )
            else:
                _LOGGER.error(_("Module %s failed to import."), config["name"])
        return loaded_modules