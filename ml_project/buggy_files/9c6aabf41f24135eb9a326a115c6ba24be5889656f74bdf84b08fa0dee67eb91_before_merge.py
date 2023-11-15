    def handle(self):
        from poetry.config.config import Config
        from poetry.config.config_source import ConfigSource
        from poetry.locations import CONFIG_DIR
        from poetry.utils._compat import Path
        from poetry.utils._compat import basestring
        from poetry.utils.toml_file import TomlFile

        config = Config()
        config_file = TomlFile(Path(CONFIG_DIR) / "config.toml")
        config_source = ConfigSource(config_file)
        config.merge(config_source.file.read())

        auth_config_file = TomlFile(Path(CONFIG_DIR) / "auth.toml")
        auth_config_source = ConfigSource(auth_config_file, auth_config=True)

        local_config_file = TomlFile(self.poetry.file.parent / "poetry.toml")
        if local_config_file.exists():
            config.merge(local_config_file.read())

        if self.option("local"):
            config_source = ConfigSource(local_config_file)

        if not config_file.exists():
            config_file.path.parent.mkdir(parents=True, exist_ok=True)
            config_file.touch(mode=0o0600)

        if self.option("list"):
            self._list_configuration(config.all(), config.raw())

            return 0

        setting_key = self.argument("key")
        if not setting_key:
            return 0

        if self.argument("value") and self.option("unset"):
            raise RuntimeError("You can not combine a setting value with --unset")

        # show the value if no value is provided
        if not self.argument("value") and not self.option("unset"):
            m = re.match(r"^repos?(?:itories)?(?:\.(.+))?", self.argument("key"))
            if m:
                if not m.group(1):
                    value = {}
                    if config.get("repositories") is not None:
                        value = config.get("repositories")
                else:
                    repo = config.get("repositories.{}".format(m.group(1)))
                    if repo is None:
                        raise ValueError(
                            "There is no {} repository defined".format(m.group(1))
                        )

                    value = repo

                self.line(str(value))
            else:
                values = self.unique_config_values
                if setting_key not in values:
                    raise ValueError("There is no {} setting.".format(setting_key))

                value = config.get(setting_key)

                if not isinstance(value, basestring):
                    value = json.dumps(value)

                self.line(value)

            return 0

        values = self.argument("value")

        unique_config_values = self.unique_config_values
        if setting_key in unique_config_values:
            if self.option("unset"):
                return config_source.remove_property(setting_key)

            return self._handle_single_value(
                config_source, setting_key, unique_config_values[setting_key], values
            )

        # handle repositories
        m = re.match(r"^repos?(?:itories)?(?:\.(.+))?", self.argument("key"))
        if m:
            if not m.group(1):
                raise ValueError("You cannot remove the [repositories] section")

            if self.option("unset"):
                repo = config.get("repositories.{}".format(m.group(1)))
                if repo is None:
                    raise ValueError(
                        "There is no {} repository defined".format(m.group(1))
                    )

                config_source.remove_property("repositories.{}".format(m.group(1)))

                return 0

            if len(values) == 1:
                url = values[0]

                config_source.add_property(
                    "repositories.{}.url".format(m.group(1)), url
                )

                return 0

            raise ValueError(
                "You must pass the url. "
                "Example: poetry config repositories.foo https://bar.com"
            )

        # handle auth
        m = re.match(r"^(http-basic|pypi-token)\.(.+)", self.argument("key"))
        if m:
            if self.option("unset"):
                keyring_repository_password_del(config, m.group(2))
                auth_config_source.remove_property(
                    "{}.{}".format(m.group(1), m.group(2))
                )

                return 0

            if m.group(1) == "http-basic":
                if len(values) == 1:
                    username = values[0]
                    # Only username, so we prompt for password
                    password = self.secret("Password:")
                elif len(values) != 2:
                    raise ValueError(
                        "Expected one or two arguments "
                        "(username, password), got {}".format(len(values))
                    )
                else:
                    username = values[0]
                    password = values[1]

                property_value = dict(username=username)
                try:
                    keyring_repository_password_set(m.group(2), username, password)
                except RuntimeError:
                    property_value.update(password=password)

                auth_config_source.add_property(
                    "{}.{}".format(m.group(1), m.group(2)), property_value
                )
            elif m.group(1) == "pypi-token":
                if len(values) != 1:
                    raise ValueError(
                        "Expected only one argument (token), got {}".format(len(values))
                    )

                token = values[0]

                auth_config_source.add_property(
                    "{}.{}".format(m.group(1), m.group(2)), token
                )

            return 0

        raise ValueError("Setting {} does not exist".format(self.argument("key")))