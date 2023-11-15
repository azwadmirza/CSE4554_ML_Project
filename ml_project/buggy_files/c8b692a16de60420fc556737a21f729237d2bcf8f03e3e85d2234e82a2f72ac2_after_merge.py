def feed_get_cover(book_id):
    book = db.session.query(db.Books).filter(db.Books.id == book_id).first()
    if book:
        return helper.get_book_cover(book.path)
    else:
        abort(404)