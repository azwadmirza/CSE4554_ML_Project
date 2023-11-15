    def consume(self, event):
        # type: (Mapping[str, Any]) -> None
        mirror_email(email.message_from_string(event["message"]),
                     rcpt_to=event["rcpt_to"], pre_checked=True)