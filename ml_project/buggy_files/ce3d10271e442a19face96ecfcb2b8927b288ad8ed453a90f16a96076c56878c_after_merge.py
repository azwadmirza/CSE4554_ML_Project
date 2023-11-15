    def get_current_user(self):
        """get current username"""
        if not hasattr(self, '_jupyterhub_user'):
            try:
                user = self.get_current_user_token()
                if user is None:
                    user = self.get_current_user_cookie()
                self._jupyterhub_user = user
            except Exception:
                # don't let errors here raise more than once
                self._jupyterhub_user = None
                raise
        return self._jupyterhub_user