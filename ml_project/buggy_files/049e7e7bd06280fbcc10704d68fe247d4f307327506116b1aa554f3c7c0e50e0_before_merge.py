def delete_selfservice(request, mail_id):
    rcpt = request.GET.get("rcpt", None)
    if rcpt is None:
        raise BadRequest(_("Invalid request"))
    try:
        msgrcpt = get_wrapper().get_recipient_message(rcpt, mail_id)
        msgrcpt.rs = 'D'
        msgrcpt.save()
    except Msgrcpt.DoesNotExist:
        raise BadRequest(_("Invalid request"))
    return render_to_json_response(_("Message deleted"))