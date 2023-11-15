def render_edit_book(book_id):
    db.session.connection().connection.connection.create_function("title_sort", 1, db.title_sort)
    cc = db.session.query(db.Custom_Columns).filter(db.Custom_Columns.datatype.notin_(db.cc_exceptions)).all()
    book = db.session.query(db.Books)\
        .filter(db.Books.id == book_id).filter(common_filters()).first()

    if not book:
        flash(_(u"Error opening eBook. File does not exist or file is not accessible"), category="error")
        return redirect(url_for("index"))

    for indx in range(0, len(book.languages)):
        book.languages[indx].language_name = language_table[get_locale()][book.languages[indx].lang_code]
    author_names = []
    for authr in book.authors:
        author_names.append(authr.name.replace('|', ','))

    # Option for showing convertbook button
    valid_source_formats=list()
    if config.config_ebookconverter == 2:
        for file in book.data:
            if file.format.lower() in EXTENSIONS_CONVERT:
                valid_source_formats.append(file.format.lower())

    # Determine what formats don't already exist
    allowed_conversion_formats = EXTENSIONS_CONVERT.copy()
    for file in book.data:
        try:
            allowed_conversion_formats.remove(file.format.lower())
        except Exception:
            app.logger.warning(file.format.lower() + ' already removed from list.')

    return render_title_template('book_edit.html', book=book, authors=author_names, cc=cc,
                                 title=_(u"edit metadata"), page="editbook",
                                 conversion_formats=allowed_conversion_formats,
                                 source_formats=valid_source_formats)