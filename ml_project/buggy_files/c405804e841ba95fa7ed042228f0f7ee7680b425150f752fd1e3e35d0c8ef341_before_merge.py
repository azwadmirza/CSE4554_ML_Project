    def upload_avatar_image(self, user_file: File,
                            acting_user_profile: UserProfile,
                            target_user_profile: UserProfile) -> None:
        file_path = user_avatar_path(target_user_profile)

        image_data = user_file.read()
        self.write_avatar_images(file_path, image_data)