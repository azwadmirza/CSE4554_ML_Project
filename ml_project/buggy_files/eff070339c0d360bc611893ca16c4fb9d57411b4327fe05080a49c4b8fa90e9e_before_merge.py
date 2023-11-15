    def list_profiles(self):
        self.update_profiles()
        result = [self.profile_info(p) for p in self.profiles.keys()]
        result.sort()
        return result