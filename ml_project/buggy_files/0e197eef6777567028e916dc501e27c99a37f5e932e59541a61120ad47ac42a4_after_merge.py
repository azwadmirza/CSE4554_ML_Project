    def consume(self, event):
        # type: (Mapping[str, Any]) -> None
        message = force_str(event["message"])
        mirror_email(email.message_from_string(message),
                     rcpt_to=event["rcpt_to"], pre_checked=True)