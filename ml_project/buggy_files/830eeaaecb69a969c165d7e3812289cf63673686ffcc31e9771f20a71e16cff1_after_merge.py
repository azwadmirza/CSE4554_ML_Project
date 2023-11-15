def get_cover(book_id):
    book = db.session.query(db.Books).filter(db.Books.id == book_id).first()
    return helper.get_book_cover(book.path)