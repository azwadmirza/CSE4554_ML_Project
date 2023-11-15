    def auth_complete(self, *args, **kwargs):
        # type: (*Any, **Any) -> Optional[HttpResponse]
        """
        Returning `None` from this function will redirect the browser
        to the login page.
        """
        try:
            # Call the auth_complete method of social_core.backends.oauth.BaseOAuth2
            return super(SocialAuthMixin, self).auth_complete(*args, **kwargs)  # type: ignore # monkey-patching
        except AuthFailed:
            return None
        except SocialAuthBaseException as e:
            logging.warning(str(e))
            return None