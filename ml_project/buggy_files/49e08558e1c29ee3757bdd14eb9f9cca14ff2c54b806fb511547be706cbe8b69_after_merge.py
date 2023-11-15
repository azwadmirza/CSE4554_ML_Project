    def from_credentials(cls, credentials, threads, profile_name, target_name,
                         user_cfg=None):
        """Create a profile from an existing set of Credentials and the
        remaining information.

        :param credentials Credentials: The credentials for this profile.
        :param threads int: The number of threads to use for connections.
        :param profile_name str: The profile name used for this profile.
        :param target_name str: The target name used for this profile.
        :param user_cfg Optional[dict]: The user-level config block from the
            raw profiles, if specified.
        :raises DbtProfileError: If the profile is invalid.
        :returns Profile: The new Profile object.
        """
        config = UserConfig.from_dict(user_cfg)
        profile = cls(
            profile_name=profile_name,
            target_name=target_name,
            config=config,
            threads=threads,
            credentials=credentials
        )
        profile.validate()
        return profile