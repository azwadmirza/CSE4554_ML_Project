def feed_categoryindex():
    off = request.args.get("offset") or 0
    entries = db.session.query(db.Tags).join(db.books_tags_link).join(db.Books).filter(common_filters())\
        .group_by('books_tags_link.tag').order_by(db.Tags.name).offset(off).limit(config.config_books_per_page)
    pagination = Pagination((int(off) / (int(config.config_books_per_page)) + 1), config.config_books_per_page,
                            len(db.session.query(db.Tags).all()))
    return render_xml_template('feed.xml', listelements=entries, folder='feed_category', pagination=pagination)