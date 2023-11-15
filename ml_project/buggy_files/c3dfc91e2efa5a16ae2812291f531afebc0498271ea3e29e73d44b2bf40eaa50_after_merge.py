def feed_publisherindex():
    off = request.args.get("offset") or 0
    entries = db.session.query(db.Publishers).join(db.books_publishers_link).join(db.Books).filter(common_filters())\
        .group_by(text('books_publishers_link.publisher')).order_by(db.Publishers.sort).limit(config.config_books_per_page).offset(off)
    pagination = Pagination((int(off) / (int(config.config_books_per_page)) + 1), config.config_books_per_page,
                            len(db.session.query(db.Publishers).all()))
    return render_xml_template('feed.xml', listelements=entries, folder='feed_publisher', pagination=pagination)