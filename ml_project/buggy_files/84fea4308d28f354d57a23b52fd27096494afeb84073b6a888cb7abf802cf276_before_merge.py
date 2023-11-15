def edit_book(book_id):
    # Show form
    if request.method != 'POST':
        return render_edit_book(book_id)

    # create the function for sorting...
    db.session.connection().connection.connection.create_function("title_sort", 1, db.title_sort)
    book = db.session.query(db.Books)\
        .filter(db.Books.id == book_id).filter(common_filters()).first()

    # Book not found
    if not book:
        flash(_(u"Error opening eBook. File does not exist or file is not accessible"), category="error")
        return redirect(url_for("index"))

    upload_single_file(request, book, book_id)
    upload_cover(request, book)
    try:
        to_save = request.form.to_dict()
        # Update book
        edited_books_id = None
        #handle book title
        if book.title != to_save["book_title"].rstrip().strip():
            if to_save["book_title"] == '':
                to_save["book_title"] = _(u'unknown')
            book.title = to_save["book_title"].rstrip().strip()
            edited_books_id = book.id

        # handle author(s)
        input_authors = to_save["author_name"].split('&')
        input_authors = list(map(lambda it: it.strip().replace(',', '|'), input_authors))
        # we have all author names now
        if input_authors == ['']:
            input_authors = [_(u'unknown')]  # prevent empty Author
        if book.authors:
            author0_before_edit = book.authors[0].name
        else:
            author0_before_edit = db.Authors(_(u'unknown'), '', 0)
        modify_database_object(input_authors, book.authors, db.Authors, db.session, 'author')
        if book.authors:
            if author0_before_edit != book.authors[0].name:
                edited_books_id = book.id
                book.author_sort = helper.get_sorted_author(input_authors[0])

        if config.config_use_google_drive:
            gdriveutils.updateGdriveCalibreFromLocal()

        error = False
        if edited_books_id:
            error = helper.update_dir_stucture(edited_books_id, config.config_calibre_dir)

        if not error:
            if to_save["cover_url"]:
                if helper.save_cover(to_save["cover_url"], book.path) is True:
                    book.has_cover = 1
                else:
                    flash(_(u"Cover is not a jpg file, can't save"), category="error")

            if book.series_index != to_save["series_index"]:
                book.series_index = to_save["series_index"]

            # Handle book comments/description
            if len(book.comments):
                book.comments[0].text = to_save["description"]
            else:
                book.comments.append(db.Comments(text=to_save["description"], book=book.id))

            # Handle book tags
            input_tags = to_save["tags"].split(',')
            input_tags = list(map(lambda it: it.strip(), input_tags))
            modify_database_object(input_tags, book.tags, db.Tags, db.session, 'tags')

            # Handle book series
            input_series = [to_save["series"].strip()]
            input_series = [x for x in input_series if x != '']
            modify_database_object(input_series, book.series, db.Series, db.session, 'series')

            if to_save["pubdate"]:
                try:
                    book.pubdate = datetime.datetime.strptime(to_save["pubdate"], "%Y-%m-%d")
                except ValueError:
                    book.pubdate = db.Books.DEFAULT_PUBDATE
            else:
                book.pubdate = db.Books.DEFAULT_PUBDATE

            if to_save["publisher"]:
                publisher = to_save["publisher"].rstrip().strip()
                if len(book.publishers) == 0 or (len(book.publishers) > 0 and publisher != book.publishers[0].name):
                    modify_database_object([publisher], book.publishers, db.Publishers, db.session, 'publisher')
            elif len(book.publishers):
                modify_database_object([], book.publishers, db.Publishers, db.session, 'publisher')


            # handle book languages
            input_languages = to_save["languages"].split(',')
            input_languages = [x.strip().lower() for x in input_languages if x != '']
            input_l = []
            invers_lang_table = [x.lower() for x in language_table[get_locale()].values()]
            for lang in input_languages:
                try:
                    res = list(language_table[get_locale()].keys())[invers_lang_table.index(lang)]
                    input_l.append(res)
                except ValueError:
                    app.logger.error('%s is not a valid language' % lang)
                    flash(_(u"%(langname)s is not a valid language", langname=lang), category="error")
            modify_database_object(input_l, book.languages, db.Languages, db.session, 'languages')

            # handle book ratings
            if to_save["rating"].strip():
                old_rating = False
                if len(book.ratings) > 0:
                    old_rating = book.ratings[0].rating
                ratingx2 = int(float(to_save["rating"]) * 2)
                if ratingx2 != old_rating:
                    is_rating = db.session.query(db.Ratings).filter(db.Ratings.rating == ratingx2).first()
                    if is_rating:
                        book.ratings.append(is_rating)
                    else:
                        new_rating = db.Ratings(rating=ratingx2)
                        book.ratings.append(new_rating)
                    if old_rating:
                        book.ratings.remove(book.ratings[0])
            else:
                if len(book.ratings) > 0:
                    book.ratings.remove(book.ratings[0])

            # handle cc data
            edit_cc_data(book_id, book, to_save)

            db.session.commit()
            if config.config_use_google_drive:
                gdriveutils.updateGdriveCalibreFromLocal()
            if "detail_view" in to_save:
                return redirect(url_for('show_book', book_id=book.id))
            else:
                flash(_("Metadata successfully updated"), category="success")
                return render_edit_book(book_id)
        else:
            db.session.rollback()
            flash(error, category="error")
            return render_edit_book(book_id)
    except Exception as e:
        app.logger.exception(e)
        db.session.rollback()
        flash(_("Error editing book, please check logfile for details"), category="error")
        return redirect(url_for('show_book', book_id=book.id))