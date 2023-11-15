def send_mails(mails):
    """Send multiple mails in single connection."""
    with get_connection() as connection:
        for mail in mails:
            email = EmailMultiAlternatives(
                settings.EMAIL_SUBJECT_PREFIX + mail['subject'],
                html2text(mail['body']),
                to=[mail['address']],
                headers=mail['headers'],
                connection=connection,
            )
            email.attach_alternative(mail['body'], 'text/html')
            email.send()