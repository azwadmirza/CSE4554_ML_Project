def fill_indexpage(page, database, db_filter, order, *join):
    if current_user.show_detail_random():
        randm = db.session.query(db.Books).filter(common_filters())\
            .order_by(func.random()).limit(config.config_random_books)
    else:
        randm = false()
    off = int(int(config.config_books_per_page) * (page - 1))
    pagination = Pagination(page, config.config_books_per_page,
                            len(db.session.query(database)
                            .filter(db_filter).filter(common_filters()).all()))
    entries = db.session.query(database).join(*join,isouter=True).filter(db_filter)\
            .filter(common_filters()).order_by(*order).offset(off).limit(config.config_books_per_page).all()
    for book in entries:
        book = order_authors(book)
    return entries, randm, pagination