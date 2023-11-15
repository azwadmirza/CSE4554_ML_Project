def viewheaders(request, mail_id):
    """Display message headers."""
    content = ""
    for qm in get_connector().get_mail_content(mail_id):
        content += qm.mail_text
    if type(content) is unicode:
        content = content.encode("utf-8")
    msg = email.message_from_string(content)
    headers = []
    for name, value in msg.items():
        if value:
            result = chardet.detect(value)
            if result["encoding"] is not None:
                value = value.decode(result["encoding"])
        headers += [(name, value)]
    return render(request, 'amavis/viewheader.html', {
        "headers": headers
    })