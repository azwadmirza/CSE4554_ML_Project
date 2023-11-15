def category_list():
    if current_user.show_category():
        entries = db.session.query(db.Tags, func.count('books_tags_link.book').label('count'))\
            .join(db.books_tags_link).join(db.Books).order_by(db.Tags.name).filter(common_filters())\
            .group_by(text('books_tags_link.tag')).all()
        return render_title_template('list.html', entries=entries, folder='category',
                                     title=_(u"Category list"), page="catlist")
    else:
        abort(404)