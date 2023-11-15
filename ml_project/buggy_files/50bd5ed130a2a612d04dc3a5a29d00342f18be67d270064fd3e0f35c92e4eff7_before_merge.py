def series_list():
    if current_user.show_series():
        entries = db.session.query(db.Series, func.count('books_series_link.book').label('count'))\
            .join(db.books_series_link).join(db.Books).filter(common_filters())\
            .group_by('books_series_link.series').order_by(db.Series.sort).all()
        return render_title_template('list.html', entries=entries, folder='series',
                                     title=_(u"Series list"), page="serieslist")
    else:
        abort(404)