    def is_valid(self):
        if not self.runner_name:
            ErrorDialog(_("Runner not provided"))
            return False
        if not self.name_entry.get_text():
            ErrorDialog(_("Please fill in the name"))
            return False
        if (self.runner_name in ("steam", "winesteam") and self.lutris_config.game_config.get("appid") is None):
            ErrorDialog(_("Steam AppId not provided"))
            return False
        invalid_fields = []
        runner_class = import_runner(self.runner_name)
        runner_instance = runner_class()
        for config in ["game", "runner"]:
            for k, v in getattr(self.lutris_config, config + "_config").items():
                option = runner_instance.find_option(config + "_options", k)
                if option is None:
                    continue
                validator = option.get("validator")
                if validator is not None:
                    try:
                        res = validator(v)
                        logger.debug("%s validated successfully: %s", k, res)
                    except Exception:
                        invalid_fields.append(option.get("label"))
        if invalid_fields:
            ErrorDialog(_("The following fields have invalid values: ") + ", ".join(invalid_fields))
            return False
        return True