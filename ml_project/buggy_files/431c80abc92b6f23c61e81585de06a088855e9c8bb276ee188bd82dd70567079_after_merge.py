def mail_admins_contact(subject, message, context, sender):
    '''
    Sends a message to the admins, as defined by the ADMINS setting.
    '''
    weblate.logger.info(
        'contact from from %s: %s',
        email,
        subject,
    )
    if not settings.ADMINS:
        return

    mail = EmailMultiAlternatives(
        u'%s%s' % (settings.EMAIL_SUBJECT_PREFIX, subject % context),
        message % context,
        to=[a[1] for a in settings.ADMINS],
        headers={'Reply-To': sender},
    )

    mail.send(fail_silently=False)