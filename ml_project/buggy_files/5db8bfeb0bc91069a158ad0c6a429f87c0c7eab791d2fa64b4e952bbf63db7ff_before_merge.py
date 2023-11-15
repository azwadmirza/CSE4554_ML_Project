def feed_seriesindex():
    off = request.args.get("offset") or 0
    entries = db.session.query(db.Series).join(db.books_series_link).join(db.Books).filter(common_filters())\
        .group_by('books_series_link.series').order_by(db.Series.sort).offset(off).all()
    pagination = Pagination((int(off) / (int(config.config_books_per_page)) + 1), config.config_books_per_page,
                            len(db.session.query(db.Series).all()))
    return render_xml_template('feed.xml', listelements=entries, folder='feed_series', pagination=pagination)