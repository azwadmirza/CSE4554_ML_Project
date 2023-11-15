def release(request, mail_id):
    """Release message selection.

    :param str mail_id: message unique identifier
    """
    mail_id = check_mail_id(request, mail_id)
    msgrcpts = []
    wrapper = get_wrapper()
    mb = Mailbox.objects.get(user=request.user) \
        if request.user.group == 'SimpleUsers' else None
    for mid in mail_id:
        r, i = mid.split()
        if mb is not None and r != mb.full_address \
                and not r in mb.alias_addresses:
            continue
        msgrcpts += [wrapper.get_recipient_message(r, i)]
    if mb is not None and parameters.get_admin("USER_CAN_RELEASE") == "no":
        # FIXME : can't use this syntax because extra SQL (using
        # .extra() for postgres) is not propagated (the 'tables'
        # parameter is lost somewhere...)
        #
        # msgrcpts.update(rs='p')
        for msgrcpt in msgrcpts:
            msgrcpt.rs = 'p'
            msgrcpt.save()
        message = ungettext("%(count)d request sent",
                            "%(count)d requests sent",
                            len(mail_id)) % {"count": len(mail_id)}
        return ajax_response(
            request, "ok", respmsg=message,
            url=QuarantineNavigationParameters(request).back_to_listing()
        )

    amr = AMrelease()
    error = None
    for rcpt in msgrcpts:
        result = amr.sendreq(rcpt.mail.mail_id, rcpt.mail.secret_id, rcpt.rid.email)
        if result:
            rcpt.rs = 'R'
            rcpt.save()
        else:
            error = result
            break

    if not error:
        message = ungettext("%(count)d message released successfully",
                            "%(count)d messages released successfully",
                            len(mail_id)) % {"count": len(mail_id)}
    else:
        message = error
    return ajax_response(
        request, "ko" if error else "ok", respmsg=message,
        url=QuarantineNavigationParameters(request).back_to_listing()
    )