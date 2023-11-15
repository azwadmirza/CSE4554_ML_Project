def mark_messages(request, selection, mtype, recipient_db=None):
    """Mark a selection of messages as spam.

    :param str selection: message unique identifier
    :param str mtype: type of marking (spam or ham)
    """
    if not manual_learning_enabled(request.user):
        return render_to_json_response({"status": "ok"})
    if recipient_db is None:
        recipient_db = (
            "user" if request.user.group == "SimpleUsers" else "global"
        )
    selection = check_mail_id(request, selection)
    connector = get_connector()
    saclient = SpamassassinClient(request.user, recipient_db)
    for item in selection:
        rcpt, mail_id = item.split()
        content = "".join(
            [msg.mail_text for msg in connector.get_mail_content(mail_id)]
        )
        result = saclient.learn_spam(rcpt, content) if mtype == "spam" \
            else saclient.learn_ham(rcpt, content)
        if not result:
            break
        connector.set_msgrcpt_status(rcpt, mail_id, mtype[0].upper())
    if saclient.error is None:
        saclient.done()
        message = ungettext("%(count)d message processed successfully",
                            "%(count)d messages processed successfully",
                            len(selection)) % {"count": len(selection)}
    else:
        message = saclient.error
    status = 400 if saclient.error else 200
    return render_to_json_response({
        "message": message, "reload": True
    }, status=status)