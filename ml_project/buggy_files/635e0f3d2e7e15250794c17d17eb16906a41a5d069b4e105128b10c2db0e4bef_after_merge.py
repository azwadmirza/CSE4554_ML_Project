def series(book_id, page):
    name = db.session.query(db.Series).filter(db.Series.id == book_id).first()
    if name:
        entries, random, pagination = fill_indexpage(page, db.Books, db.Books.series.any(db.Series.id == book_id),
                                                 [db.Books.series_index])
        return render_title_template('index.html', random=random, pagination=pagination, entries=entries,
                                     title=_(u"Series: %(serie)s", serie=name.name), page="series")
    else:
        abort(404)