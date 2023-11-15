    def msg(self):
        """Get message's content."""
        import email

        if self._msg is None:
            qmails = get_connector().get_mail_content(self.mailid)
            mail_text = "".join([qm.mail_text for qm in qmails])
            if type(mail_text) is unicode:
                mail_text = mail_text.encode("utf-8")
            self._msg = email.message_from_string(mail_text)
            self._parse(self._msg)
        return self._msg