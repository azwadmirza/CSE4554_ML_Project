def publisher_list():
    if current_user.show_publisher():
        entries = db.session.query(db.Publishers, func.count('books_publishers_link.book').label('count'))\
            .join(db.books_publishers_link).join(db.Books).filter(common_filters())\
            .group_by(text('books_publishers_link.publisher')).order_by(db.Publishers.sort).all()
        return render_title_template('list.html', entries=entries, folder='publisher',
                                     title=_(u"Publisher list"), page="publisherlist")
    else:
        abort(404)