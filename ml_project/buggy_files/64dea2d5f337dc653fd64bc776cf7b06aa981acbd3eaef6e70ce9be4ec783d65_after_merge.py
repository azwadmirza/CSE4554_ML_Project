def delete(request, mail_id):
    """Delete message selection.

    :param str mail_id: message unique identifier
    """
    mail_id = check_mail_id(request, mail_id)
    wrapper = get_wrapper()
    mb = Mailbox.objects.get(user=request.user) \
        if request.user.group == 'SimpleUsers' else None
    for mid in mail_id:
        r, i = mid.split()
        if mb is not None and r != mb.full_address \
                and not r in mb.alias_addresses:
            continue
        wrapper.set_msgrcpt_status(r, i, 'D')
    message = ungettext("%(count)d message deleted successfully",
                        "%(count)d messages deleted successfully",
                        len(mail_id)) % {"count": len(mail_id)}
    return ajax_response(
        request, respmsg=message,
        url=QuarantineNavigationParameters(request).back_to_listing()
    )