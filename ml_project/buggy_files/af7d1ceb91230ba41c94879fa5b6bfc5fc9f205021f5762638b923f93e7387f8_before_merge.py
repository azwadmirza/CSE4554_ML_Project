def send_email_sendgrid(sender, subject, message, recipients, image_png):
    import sendgrid as sendgrid_lib
    client = sendgrid_lib.SendGridClient(
        sendgrid().username, sendgrid().password, raise_errors=True)
    to_send = sendgrid_lib.Mail()
    to_send.add_to(recipients)
    to_send.set_from(sender)
    to_send.set_subject(subject)
    if email().format == 'html':
        to_send.set_html(message)
    else:
        to_send.set_text(message)
    if image_png:
        to_send.add_attachment(image_png)

    client.send(to_send)