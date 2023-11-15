def feed_authorindex():
    off = request.args.get("offset") or 0
    entries = db.session.query(db.Authors).join(db.books_authors_link).join(db.Books).filter(common_filters())\
        .group_by(text('books_authors_link.author')).order_by(db.Authors.sort).limit(config.config_books_per_page).offset(off)
    pagination = Pagination((int(off) / (int(config.config_books_per_page)) + 1), config.config_books_per_page,
                            len(db.session.query(db.Authors).all()))
    return render_xml_template('feed.xml', listelements=entries, folder='feed_author', pagination=pagination)