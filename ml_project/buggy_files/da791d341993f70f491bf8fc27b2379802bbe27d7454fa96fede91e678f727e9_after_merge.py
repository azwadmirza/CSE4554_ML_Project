def release_selfservice(request, mail_id):
    rcpt = request.GET.get("rcpt", None)
    secret_id = request.GET.get("secret_id", None)
    if rcpt is None or secret_id is None:
        raise BadRequest(_("Invalid request"))
    wrapper = get_wrapper()
    try:
        msgrcpt = wrapper.get_recipient_message(rcpt, mail_id)
    except Msgrcpt.DoesNotExist:
        raise BadRequest(_("Invalid request"))
    if secret_id != msgrcpt.mail.secret_id:
        raise BadRequest(_("Invalid request"))
    if parameters.get_admin("USER_CAN_RELEASE") == "no":
        wrapper.set_msgrcpt_status(rcpt, mail_id, 'p')
        msg = _("Request sent")
    else:
        amr = AMrelease()
        result = amr.sendreq(mail_id, secret_id, rcpt)
        if result:
            wrapper.set_msgrcpt_status(rcpt, mail_id, 'R')
            msg = _("Message released")
        else:
            raise BadRequest(result)
    return render_to_json_response(msg)