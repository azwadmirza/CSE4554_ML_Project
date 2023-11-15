    def to_profile_info(self, serialize_credentials=False):
        """Unlike to_project_config, this dict is not a mirror of any existing
        on-disk data structure. It's used when creating a new profile from an
        existing one.

        :param serialize_credentials bool: If True, serialize the credentials.
            Otherwise, the Credentials object will be copied.
        :returns dict: The serialized profile.
        """
        result = {
            'profile_name': self.profile_name,
            'target_name': self.target_name,
            'config': self.config.to_dict(),
            'threads': self.threads,
            'credentials': self.credentials.incorporate(),
        }
        if serialize_credentials:
            result['credentials'] = result['credentials'].serialize()
        return result