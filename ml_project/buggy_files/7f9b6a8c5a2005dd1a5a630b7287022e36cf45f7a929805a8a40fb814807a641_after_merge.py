    def upload_avatar_image(self, user_file: File,
                            acting_user_profile: UserProfile,
                            target_user_profile: UserProfile,
                            content_type: Optional[str] = None) -> None:
        if content_type is None:
            content_type = guess_type(user_file.name)[0]
        s3_file_name = user_avatar_path(target_user_profile)

        image_data = user_file.read()
        self.write_avatar_images(s3_file_name, target_user_profile,
                                 image_data, content_type)