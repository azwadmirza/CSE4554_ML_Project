def send_mail(frm, to, subject, body, config, html=None):
    """
    Sends an email.

    :type  frm: str
    :param frm: from address

    :type  to: str
    :param to: to address

    :type  subject: str
    :param subject: Subject line

    :type  body: str
    :param body: Body text (should be plain text)

    :type  config: object
    :param config: Galaxy configuration object

    :type  html: str
    :param html: Alternative HTML representation of the body content. If
                 provided will convert the message to a MIMEMultipart. (Default 'None')
    """

    to = listify(to)
    if html:
        msg = MIMEMultipart('alternative')
    else:
        msg = MIMEText(body, 'plain', 'utf-8')

    msg['To'] = ', '.join(to)
    msg['From'] = frm
    msg['Subject'] = subject

    if config.smtp_server is None:
        log.error("Mail is not configured for this Galaxy instance.")
        log.info(msg)
        return

    if html:
        mp_text = MIMEText(body, 'plain', 'utf-8')
        mp_html = MIMEText(html, 'html', 'utf-8')
        msg.attach(mp_text)
        msg.attach(mp_html)

    smtp_ssl = asbool(getattr(config, 'smtp_ssl', False))
    if smtp_ssl:
        s = smtplib.SMTP_SSL()
    else:
        s = smtplib.SMTP()
    s.connect(config.smtp_server)
    if not smtp_ssl:
        try:
            s.starttls()
            log.debug('Initiated SSL/TLS connection to SMTP server: %s' % config.smtp_server)
        except RuntimeError as e:
            log.warning('SSL/TLS support is not available to your Python interpreter: %s' % e)
        except smtplib.SMTPHeloError as e:
            log.error("The server didn't reply properly to the HELO greeting: %s" % e)
            s.close()
            raise
        except smtplib.SMTPException as e:
            log.warning('The server does not support the STARTTLS extension: %s' % e)
    if config.smtp_username and config.smtp_password:
        try:
            s.login(config.smtp_username, config.smtp_password)
        except smtplib.SMTPHeloError as e:
            log.error("The server didn't reply properly to the HELO greeting: %s" % e)
            s.close()
            raise
        except smtplib.SMTPAuthenticationError as e:
            log.error("The server didn't accept the username/password combination: %s" % e)
            s.close()
            raise
        except smtplib.SMTPException as e:
            log.error("No suitable authentication method was found: %s" % e)
            s.close()
            raise
    s.sendmail(frm, to, msg.as_string())
    s.quit()