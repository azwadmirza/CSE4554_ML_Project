    def from_args(cls, args, project_profile_name=None, cli_vars=None):
        """Given the raw profiles as read from disk and the name of the desired
        profile if specified, return the profile component of the runtime
        config.

        :param args argparse.Namespace: The arguments as parsed from the cli.
        :param cli_vars dict: The command-line variables passed as arguments,
            as a dict.
        :param project_profile_name Optional[str]: The profile name, if
            specified in a project.
        :raises DbtProjectError: If there is no profile name specified in the
            project or the command line arguments, or if the specified profile
            is not found
        :raises DbtProfileError: If the profile is invalid or missing, or the
            target could not be found.
        :returns Profile: The new Profile object.
        """
        if cli_vars is None:
            cli_vars = dbt.utils.parse_cli_vars(getattr(args, 'vars', '{}'))

        threads_override = getattr(args, 'threads', None)
        # TODO(jeb): is it even possible for this to not be set?
        profiles_dir = getattr(args, 'profiles_dir', PROFILES_DIR)
        target_override = getattr(args, 'target', None)
        raw_profiles = read_profile(profiles_dir)
        profile_name = cls.pick_profile_name(args.profile,
                                             project_profile_name)

        return cls.from_raw_profiles(
            raw_profiles=raw_profiles,
            profile_name=profile_name,
            cli_vars=cli_vars,
            target_override=target_override,
            threads_override=threads_override
        )