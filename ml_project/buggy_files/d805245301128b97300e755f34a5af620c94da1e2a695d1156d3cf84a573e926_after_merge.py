    def get_core_conf(cls, force_registration: bool = False, allow_old: bool = False):
        """Get a Config instance for the core bot.

        All core modules that require a config instance should use this
        classmethod instead of `get_conf`.

        Parameters
        ----------
        force_registration : `bool`, optional
            See `force_registration`.

        """
        return cls.get_conf(
            None,
            cog_name="Core",
            identifier=0,
            force_registration=force_registration,
            allow_old=allow_old,
        )