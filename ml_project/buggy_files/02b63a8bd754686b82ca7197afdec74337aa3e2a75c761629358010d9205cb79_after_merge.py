    def get_mail_content(self, mailid):
        """Retrieve the content of a message."""
        content = "".join([
            str(qmail.mail_text)
            for qmail in Quarantine.objects.filter(mail=mailid)
        ])
        if isinstance(content, unicode):
            content = content.encode("utf-8")
        return content