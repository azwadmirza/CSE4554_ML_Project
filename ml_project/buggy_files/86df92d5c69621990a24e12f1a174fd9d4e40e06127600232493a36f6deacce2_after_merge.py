def author(book_id, page):
    entries, __, pagination = fill_indexpage(page, db.Books, db.Books.authors.any(db.Authors.id == book_id),
                                            [db.Series.name, db.Books.series_index],db.books_series_link, db.Series)
    if entries is None:
        flash(_(u"Error opening eBook. File does not exist or file is not accessible:"), category="error")
        return redirect(url_for("index"))

    name = (db.session.query(db.Authors).filter(db.Authors.id == book_id).first().name).replace('|', ',')

    author_info = None
    other_books = []
    if goodreads_support and config.config_use_goodreads:
        try:
            gc = GoodreadsClient(config.config_goodreads_api_key, config.config_goodreads_api_secret)
            author_info = gc.find_author(author_name=name)
            other_books = get_unique_other_books(entries.all(), author_info.books)
        except Exception:
            # Skip goodreads, if site is down/inaccessible
            app.logger.error('Goodreads website is down/inaccessible')

    return render_title_template('author.html', entries=entries, pagination=pagination,
                                 title=name, author=author_info, other_books=other_books, page="author",
                                 config_authors_max=config.config_authors_max)