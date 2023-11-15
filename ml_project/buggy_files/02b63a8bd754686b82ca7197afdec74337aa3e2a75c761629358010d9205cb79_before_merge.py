    def get_mail_content(self, mailid):
        """Retrieve the content of a message.
        """
        return Quarantine.objects.filter(mail=mailid)