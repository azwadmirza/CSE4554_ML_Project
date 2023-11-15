def show_book(book_id):
    entries = db.session.query(db.Books).filter(db.Books.id == book_id).filter(common_filters()).first()
    if entries:
        for index in range(0, len(entries.languages)):
            try:
                entries.languages[index].language_name = LC.parse(entries.languages[index].lang_code).get_language_name(
                    get_locale())
            except UnknownLocaleError:
                entries.languages[index].language_name = _(
                    isoLanguages.get(part3=entries.languages[index].lang_code).name)
        tmpcc = db.session.query(db.Custom_Columns).filter(db.Custom_Columns.datatype.notin_(db.cc_exceptions)).all()

        if config.config_columns_to_ignore:
            cc = []
            for col in tmpcc:
                r = re.compile(config.config_columns_to_ignore)
                if r.match(col.label):
                    cc.append(col)
        else:
            cc = tmpcc
        book_in_shelfs = []
        shelfs = ub.session.query(ub.BookShelf).filter(ub.BookShelf.book_id == book_id).all()
        for entry in shelfs:
            book_in_shelfs.append(entry.shelf)

        if not current_user.is_anonymous:
            if not config.config_read_column:
                matching_have_read_book = ub.session.query(ub.ReadBook)\
                    .filter(ub.and_(ub.ReadBook.user_id == int(current_user.id),
                    ub.ReadBook.book_id == book_id)).all()
                have_read = len(matching_have_read_book) > 0 and matching_have_read_book[0].is_read
            else:
                try:
                    matching_have_read_book = getattr(entries,'custom_column_'+str(config.config_read_column))
                    have_read = len(matching_have_read_book) > 0 and matching_have_read_book[0].value
                except KeyError:
                    app.logger.error(
                        u"Custom Column No.%d is not exisiting in calibre database" % config.config_read_column)
                    have_read = None

        else:
            have_read = None

        entries.tags = sort(entries.tags, key = lambda tag: tag.name)

        return render_title_template('detail.html', entry=entries, cc=cc, is_xhr=request.is_xhr,
                                     title=entries.title, books_shelfs=book_in_shelfs,
                                     have_read=have_read, page="book")
    else:
        flash(_(u"Error opening eBook. File does not exist or file is not accessible:"), category="error")
        return redirect(url_for("index"))