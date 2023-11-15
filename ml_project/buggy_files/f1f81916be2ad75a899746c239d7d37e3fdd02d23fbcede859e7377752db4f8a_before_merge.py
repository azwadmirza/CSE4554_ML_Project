    def authenticate(self, username=None, password=None):
        """Check the username/password and return a User."""
        host = getattr(settings, "AUTH_SMTP_SERVER_ADDRESS", "localhost")
        port = getattr(settings, "AUTH_SMTP_SERVER_PORT", 25)
        secured_mode = getattr(settings, "AUTH_SMTP_SECURED_MODE", None)
        if secured_mode == "ssl":
            smtp = smtplib.SMTP_SSL(host, port)
        else:
            smtp = smtplib.SMTP(host, port)
            if secured_mode == "starttls":
                smtp.starttls()
        try:
            smtp.login(username, password)
        except smtplib.SMTPException:
            return None
        return self.get_or_build_user(username)