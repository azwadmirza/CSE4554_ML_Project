def send_mails(mails):
    """Send multiple mails in single connection."""
    connection = get_connection()
    try:
        connection.open()
    except Exception as error:
        report_error(error, prefix='Failed to send notifications')
        connection.close()
        return

    try:
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
    finally:
        connection.close()