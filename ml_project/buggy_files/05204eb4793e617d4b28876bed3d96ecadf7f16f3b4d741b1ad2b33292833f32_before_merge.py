    def get_mail_content(self, mailid):
        """Retrieve the content of a message."""
        return Quarantine.objects.filter(mail=mailid).extra(
            select={'mail_text': "convert_from(mail_text, 'UTF8')"}
        )