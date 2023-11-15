    def __init__(
        self,
        app=None,
        instance_relative_config=False,
        dynaconf_instance=None,
        **kwargs,
    ):
        """kwargs holds initial dynaconf configuration"""
        if not flask_installed:  # pragma: no cover
            raise RuntimeError(
                "To use this extension Flask must be installed "
                "install it with: pip install flask"
            )
        self.kwargs = kwargs

        kwargs.setdefault("ENVVAR_PREFIX", "FLASK")
        env_prefix = f"{kwargs['ENVVAR_PREFIX']}_ENV"  # FLASK_ENV
        kwargs.setdefault("ENV_SWITCHER", env_prefix)
        kwargs.setdefault("ENVIRONMENTS", True)
        kwargs.setdefault("load_dotenv", True)
        kwargs.setdefault(
            "default_settings_paths", dynaconf.DEFAULT_SETTINGS_FILES
        )

        self.dynaconf_instance = dynaconf_instance
        self.instance_relative_config = instance_relative_config
        if app:
            self.init_app(app, **kwargs)