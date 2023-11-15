def viewmail(request, mail_id):
    rcpt = request.GET["rcpt"]
    if request.user.mailbox_set.count():
        mb = Mailbox.objects.get(user=request.user)
        if rcpt in mb.alias_addresses:
            msgrcpt = get_wrapper().get_recipient_message(rcpt, mail_id)
            msgrcpt.rs = 'V'
            msgrcpt.save()

    content = Template("""
<iframe src="{{ url }}" id="mailcontent"></iframe>
""").render(Context({"url": reverse(getmailcontent, args=[mail_id])}))
    menu = viewm_menu(mail_id, rcpt)
    ctx = getctx("ok", menu=menu, listing=content)
    request.session['location'] = 'viewmail'
    return render_to_json_response(ctx)