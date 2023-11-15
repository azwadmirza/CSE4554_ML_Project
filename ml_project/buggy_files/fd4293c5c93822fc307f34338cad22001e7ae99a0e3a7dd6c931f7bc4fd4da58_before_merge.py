def index(page):
    entries, random, pagination = fill_indexpage(page, db.Books, True, [db.Books.timestamp.desc()])
    return render_title_template('index.html', random=random, entries=entries, pagination=pagination,
                                 title=_(u"Recently Added Books"), page="root")