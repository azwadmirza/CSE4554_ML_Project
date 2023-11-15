    def extra_preferences(self):
        data = {}
        extra_user_preferences = self.preferences.get('extra_user_preferences')
        if extra_user_preferences:
            try:
                data = json.loads(extra_user_preferences)
            except Exception:
                pass
        return data