def send_mail(book_id, book_format, convert, kindle_mail, calibrepath, user_id):
    """Send email with attachments"""
    book = db.session.query(db.Books).filter(db.Books.id == book_id).first()

    if convert:
        # returns None if success, otherwise errormessage
        return convert_book_format(book_id, calibrepath, u'epub', book_format.lower(), user_id, kindle_mail)
    else:
        for entry in iter(book.data):
            if entry.format.upper() == book_format.upper():
                result = entry.name + '.' + book_format.lower()
                global_WorkerThread.add_email(_(u"Send to Kindle"), book.path, result, ub.get_mail_settings(),
                                      kindle_mail, user_id, _(u"E-mail: %(book)s", book=book.title),
                                      _(u'This e-mail has been sent via Calibre-Web.'))
                return
        return _(u"The requested file could not be read. Maybe wrong permissions?")