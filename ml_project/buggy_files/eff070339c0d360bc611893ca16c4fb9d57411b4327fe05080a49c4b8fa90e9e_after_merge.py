    def list_profiles(self):
        self.update_profiles()
        result = [self.profile_info(p) for p in sorted(self.profiles.keys())]
        return result