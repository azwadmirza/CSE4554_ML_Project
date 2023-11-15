    def upload_avatar_image(self, user_file: File,
                            acting_user_profile: UserProfile,
                            target_user_profile: UserProfile,
                            content_type: Optional[str]=None) -> None:
        raise NotImplementedError()