def send_mail(book_id, kindle_mail, calibrepath, user_id):
    """Send email with attachments"""
    book = db.session.query(db.Books).filter(db.Books.id == book_id).first()
    data = db.session.query(db.Data).filter(db.Data.book == book.id).all()

    formats = {}
    for entry in data:
        if entry.format == "MOBI":
            formats["mobi"] = entry.name + ".mobi"
        if entry.format == "EPUB":
            formats["epub"] = entry.name + ".epub"
        if entry.format == "PDF":
            formats["pdf"] = entry.name + ".pdf"

    if len(formats) == 0:
        return _(u"Could not find any formats suitable for sending by e-mail")

    if 'mobi' in formats:
        result = formats['mobi']
    elif 'epub' in formats:
        # returns None if success, otherwise errormessage
        return convert_book_format(book_id, calibrepath, u'epub', u'mobi', user_id, kindle_mail)
    elif 'pdf' in formats:
        result = formats['pdf'] # worker.get_attachment()
    else:
        return _(u"Could not find any formats suitable for sending by e-mail")
    if result:
        global_WorkerThread.add_email(_(u"Send to Kindle"), book.path, result, ub.get_mail_settings(),
                                      kindle_mail, user_id, _(u"E-mail: %(book)s", book=book.title),
                                      _(u'This e-mail has been sent via Calibre-Web.'))
    else:
        return _(u"The requested file could not be read. Maybe wrong permissions?")