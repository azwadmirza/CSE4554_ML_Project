def author_list():
    if current_user.show_author():
        entries = db.session.query(db.Authors, func.count('books_authors_link.book').label('count'))\
            .join(db.books_authors_link).join(db.Books).filter(common_filters())\
            .group_by('books_authors_link.author').order_by(db.Authors.sort).all()
        for entry in entries:
            entry.Authors.name = entry.Authors.name.replace('|', ',')
        return render_title_template('list.html', entries=entries, folder='author',
                                     title=_(u"Author list"), page="authorlist")
    else:
        abort(404)