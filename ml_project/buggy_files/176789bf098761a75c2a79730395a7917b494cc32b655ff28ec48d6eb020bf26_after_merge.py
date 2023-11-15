def viewheaders(request, mail_id):
    """Display message headers."""
    content = get_connector().get_mail_content(mail_id)
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