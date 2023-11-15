    def msg(self):
        """Get message's content."""
        import email

        if self._msg is None:
            mail_text = get_connector().get_mail_content(self.mailid)
            self._msg = email.message_from_string(mail_text)
            self._parse(self._msg)
        return self._msg