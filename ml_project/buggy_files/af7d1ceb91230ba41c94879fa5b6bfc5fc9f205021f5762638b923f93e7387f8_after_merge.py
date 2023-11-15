def send_email_sendgrid(sender, subject, message, recipients, image_png):
    import sendgrid as sendgrid_lib
    client = sendgrid_lib.SendGridAPIClient(sendgrid().apikey)

    to_send = sendgrid_lib.Mail(
            from_email=sender,
            to_emails=recipients,
            subject=subject)

    if email().format == 'html':
        to_send.add_content(message, 'text/html')
    else:
        to_send.add_content(message, 'text/plain')

    if image_png:
        to_send.add_attachment(image_png)

    client.send(to_send)